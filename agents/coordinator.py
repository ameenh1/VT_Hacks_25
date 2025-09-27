"""
Multi-Agent Coordination System for Real Estate Investment Platform
Manages communication between Customer Agent, Analysis Engine, and Deal Finder
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import weakref

from models.data_models import (
    AgentRequest, AgentResponse, AgentType, AnalysisRequest, 
    QuickAnalysisRequest, QuickAnalysisResponse, PropertyAnalysis
)

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentMessage:
    """Internal message structure for agent communication"""
    
    def __init__(self, request: AgentRequest, callback: Optional[Callable] = None):
        self.id = request.request_id
        self.request = request
        self.callback = callback
        self.status = MessageStatus.PENDING
        self.response: Optional[AgentResponse] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.retry_count = 0
        self.max_retries = 3
        self.timeout_seconds = 300  # 5 minutes default
    
    @property
    def age_seconds(self) -> float:
        return (datetime.now() - self.created_at).total_seconds()
    
    @property
    def processing_time_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def is_expired(self) -> bool:
        return self.age_seconds > self.timeout_seconds


class AgentCoordinator:
    """
    Central coordinator for multi-agent communication
    Manages message routing, queuing, and response handling
    """
    
    def __init__(self):
        """Initialize the agent coordinator"""
        self.agents = {}  # Registry of active agents
        self.message_queues: Dict[AgentType, asyncio.Queue] = {}
        self.pending_requests: Dict[str, AgentMessage] = {}
        self.completed_requests: Dict[str, AgentMessage] = {}
        self.agent_workers: Dict[AgentType, asyncio.Task] = {}
        
        # Metrics
        self.total_messages_processed = 0
        self.failed_messages = 0
        self.average_response_time = 0.0
        
        # Configuration
        self.max_queue_size = 1000
        self.cleanup_interval_hours = 24
        self.max_concurrent_requests_per_agent = 10
        
        logger.info("Agent Coordinator initialized")
    
    def register_agent(self, agent_type: AgentType, agent_instance: Any) -> bool:
        """Register an agent with the coordinator"""
        
        if agent_type in self.agents:
            logger.warning(f"Agent {agent_type.value} already registered, replacing")
        
        self.agents[agent_type] = weakref.ref(agent_instance)
        self.message_queues[agent_type] = asyncio.Queue(maxsize=self.max_queue_size)
        
        # Start worker task for this agent
        self.agent_workers[agent_type] = asyncio.create_task(
            self._agent_worker(agent_type)
        )
        
        logger.info(f"Agent {agent_type.value} registered successfully")
        return True
    
    def unregister_agent(self, agent_type: AgentType) -> bool:
        """Unregister an agent"""
        
        if agent_type not in self.agents:
            logger.warning(f"Agent {agent_type.value} not registered")
            return False
        
        # Cancel worker task
        if agent_type in self.agent_workers:
            self.agent_workers[agent_type].cancel()
            del self.agent_workers[agent_type]
        
        # Clean up
        del self.agents[agent_type]
        del self.message_queues[agent_type]
        
        logger.info(f"Agent {agent_type.value} unregistered")
        return True
    
    async def send_request(self, request: AgentRequest, 
                          callback: Optional[Callable] = None,
                          timeout_seconds: int = 300) -> str:
        """Send a request to an agent"""
        
        if request.target_agent not in self.agents:
            raise ValueError(f"Target agent {request.target_agent.value} not registered")
        
        # Create message
        message = AgentMessage(request, callback)
        message.timeout_seconds = timeout_seconds
        
        # Store in pending requests
        self.pending_requests[message.id] = message
        
        # Add to agent's queue based on priority
        queue = self.message_queues[request.target_agent]
        
        try:
            if request.priority >= MessagePriority.HIGH.value:
                # High priority - add to front of queue (LIFO behavior)
                queue._queue.appendleft(message)
            else:
                # Normal priority - add to back (FIFO behavior)
                await queue.put(message)
            
            logger.info(f"Request {message.id} queued for {request.target_agent.value}")
            return message.id
            
        except asyncio.QueueFull:
            logger.error(f"Queue full for agent {request.target_agent.value}")
            del self.pending_requests[message.id]
            raise RuntimeError(f"Agent {request.target_agent.value} queue is full")
    
    async def wait_for_response(self, request_id: str, timeout_seconds: int = 300) -> AgentResponse:
        """Wait for a specific request response"""
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            # Check if completed
            if request_id in self.completed_requests:
                message = self.completed_requests[request_id]
                if message.response:
                    return message.response
                else:
                    raise RuntimeError(f"Request {request_id} failed: {message.status.value}")
            
            # Check if still pending
            if request_id in self.pending_requests:
                message = self.pending_requests[request_id]
                if message.is_expired():
                    message.status = MessageStatus.TIMEOUT
                    self._complete_message(message)
                    raise TimeoutError(f"Request {request_id} timed out")
            else:
                raise ValueError(f"Request {request_id} not found")
            
            await asyncio.sleep(0.1)
        
        raise TimeoutError(f"Request {request_id} timed out waiting for response")
    
    async def send_and_wait(self, request: AgentRequest, timeout_seconds: int = 300) -> AgentResponse:
        """Send request and wait for response (convenience method)"""
        
        request_id = await self.send_request(request, timeout_seconds=timeout_seconds)
        return await self.wait_for_response(request_id, timeout_seconds)
    
    async def _agent_worker(self, agent_type: AgentType):
        """Worker task that processes messages for an agent"""
        
        logger.info(f"Starting worker for agent {agent_type.value}")
        queue = self.message_queues[agent_type]
        
        try:
            while True:
                # Get message from queue
                message = await queue.get()
                
                try:
                    await self._process_message(agent_type, message)
                except Exception as e:
                    logger.error(f"Error processing message {message.id}: {e}")
                    message.status = MessageStatus.FAILED
                    self._complete_message(message)
                finally:
                    queue.task_done()
                    
        except asyncio.CancelledError:
            logger.info(f"Worker for agent {agent_type.value} cancelled")
        except Exception as e:
            logger.error(f"Worker for agent {agent_type.value} crashed: {e}")
    
    async def _process_message(self, agent_type: AgentType, message: AgentMessage):
        """Process a single message"""
        
        message.status = MessageStatus.PROCESSING
        message.started_at = datetime.now()
        
        logger.debug(f"Processing message {message.id} for {agent_type.value}")
        
        # Get agent instance
        agent_ref = self.agents.get(agent_type)
        if not agent_ref:
            raise RuntimeError(f"Agent {agent_type.value} not found")
        
        agent_instance = agent_ref()
        if not agent_instance:
            raise RuntimeError(f"Agent {agent_type.value} instance is no longer available")
        
        try:
            # Route message based on request type and agent
            response = await self._route_message(agent_instance, message.request)
            
            # Create response
            agent_response = AgentResponse(
                request_id=message.id,
                responding_agent=agent_type,
                success=True,
                payload=response,
                timestamp=datetime.now(),
                processing_time_ms=int((datetime.now() - message.started_at).total_seconds() * 1000)
            )
            
            message.response = agent_response
            message.status = MessageStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Message processing failed for {message.id}: {e}")
            
            # Create error response
            agent_response = AgentResponse(
                request_id=message.id,
                responding_agent=agent_type,
                success=False,
                payload={},
                error_message=str(e),
                timestamp=datetime.now()
            )
            
            message.response = agent_response
            message.status = MessageStatus.FAILED
        
        finally:
            message.completed_at = datetime.now()
            self._complete_message(message)
    
    async def _route_message(self, agent_instance: Any, request: AgentRequest) -> Dict[str, Any]:
        """Route message to appropriate agent method"""
        
        if request.target_agent == AgentType.ANALYSIS_ENGINE:
            return await self._route_analysis_request(agent_instance, request)
        elif request.target_agent == AgentType.CUSTOMER_AGENT:
            return await self._route_customer_request(agent_instance, request)
        elif request.target_agent == AgentType.DEAL_FINDER:
            return await self._route_deal_finder_request(agent_instance, request)
        else:
            raise ValueError(f"Unknown target agent: {request.target_agent}")
    
    async def _route_analysis_request(self, analysis_engine: Any, request: AgentRequest) -> Dict[str, Any]:
        """Route requests to Analysis Engine"""
        
        request_type = request.request_type
        payload = request.payload
        
        if request_type == "property_analysis":
            # Full property analysis
            address = payload.get("address")
            listing_price = payload.get("listing_price")
            
            if not address:
                raise ValueError("Address required for property analysis")
            
            # Use quick analysis method for now
            result = await analysis_engine.quick_analysis(address, listing_price)
            return {"analysis_result": result}
            
        elif request_type == "quick_analysis":
            # Quick analysis
            address = payload.get("address")
            listing_price = payload.get("listing_price")
            
            result = await analysis_engine.quick_analysis(address, listing_price)
            return {"quick_analysis": result}
            
        elif request_type == "market_analysis":
            # Market analysis only
            location = payload.get("location")
            # Implement market-only analysis
            return {"market_analysis": f"Market analysis for {location}"}
            
        else:
            raise ValueError(f"Unknown analysis request type: {request_type}")
    
    async def _route_customer_request(self, customer_agent: Any, request: AgentRequest) -> Dict[str, Any]:
        """Route requests to Customer Agent"""
        
        request_type = request.request_type
        payload = request.payload
        
        if request_type == "explain_analysis":
            # Explain analysis results in simple terms
            analysis_data = payload.get("analysis_data", {})
            explanation = await customer_agent.explain_analysis_results(analysis_data)
            return {"explanation": explanation}
            
        elif request_type == "user_query":
            # Handle user question
            query = payload.get("query", "")
            context = payload.get("context", {})
            response = await customer_agent.handle_general_query(query, context)
            return {"response": response}
            
        elif request_type == "followup_question":
            # Answer follow-up questions
            question = payload.get("question", "")
            context = payload.get("context", {})
            answer = await customer_agent.answer_followup_question(question, context)
            return {"answer": answer}
            
        elif request_type == "next_steps":
            # Provide next steps
            analysis_data = payload.get("analysis_data", {})
            steps = await customer_agent.provide_next_steps(analysis_data)
            return {"next_steps": steps}
            
        else:
            raise ValueError(f"Unknown customer request type: {request_type}")
    
    async def _route_deal_finder_request(self, deal_finder: Any, request: AgentRequest) -> Dict[str, Any]:
        """Route requests to Deal Finder"""
        
        request_type = request.request_type
        payload = request.payload
        
        if request_type == "find_deals":
            # Find investment deals
            criteria = payload.get("criteria", {})
            deals = await deal_finder.find_deals(criteria)
            return {"deals": deals}
            
        elif request_type == "monitor_property":
            # Monitor specific property
            address = payload.get("address")
            await deal_finder.monitor_property(address)
            return {"status": "monitoring_started"}
            
        else:
            raise ValueError(f"Unknown deal finder request type: {request_type}")
    
    def _complete_message(self, message: AgentMessage):
        """Move message from pending to completed"""
        
        if message.id in self.pending_requests:
            del self.pending_requests[message.id]
        
        self.completed_requests[message.id] = message
        
        # Call callback if provided
        if message.callback:
            try:
                asyncio.create_task(message.callback(message.response))
            except Exception as e:
                logger.error(f"Callback failed for message {message.id}: {e}")
        
        # Update metrics
        self.total_messages_processed += 1
        if message.status == MessageStatus.FAILED:
            self.failed_messages += 1
        
        if message.processing_time_seconds:
            # Update rolling average
            self.average_response_time = (
                (self.average_response_time * (self.total_messages_processed - 1) + 
                 message.processing_time_seconds) / self.total_messages_processed
            )
        
        logger.debug(f"Message {message.id} completed with status: {message.status.value}")
    
    async def cleanup_old_messages(self):
        """Clean up old completed messages"""
        
        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_interval_hours)
        
        # Clean up completed requests
        to_remove = [
            msg_id for msg_id, message in self.completed_requests.items()
            if message.completed_at and message.completed_at < cutoff_time
        ]
        
        for msg_id in to_remove:
            del self.completed_requests[msg_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old messages")
    
    def get_agent_status(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get status information for an agent"""
        
        if agent_type not in self.agents:
            return {"status": "not_registered"}
        
        queue = self.message_queues.get(agent_type)
        worker = self.agent_workers.get(agent_type)
        
        # Count pending messages for this agent
        pending_count = sum(
            1 for msg in self.pending_requests.values()
            if msg.request.target_agent == agent_type
        )
        
        return {
            "status": "active" if worker and not worker.done() else "inactive",
            "queue_size": queue.qsize() if queue else 0,
            "pending_requests": pending_count,
            "worker_running": bool(worker and not worker.done())
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""
        
        return {
            "total_messages_processed": self.total_messages_processed,
            "failed_messages": self.failed_messages,
            "success_rate": (
                (self.total_messages_processed - self.failed_messages) / 
                max(1, self.total_messages_processed)
            ),
            "average_response_time_seconds": self.average_response_time,
            "pending_requests": len(self.pending_requests),
            "completed_requests": len(self.completed_requests),
            "registered_agents": len(self.agents),
            "active_workers": len([w for w in self.agent_workers.values() if not w.done()])
        }
    
    async def shutdown(self):
        """Graceful shutdown of the coordinator"""
        
        logger.info("Shutting down Agent Coordinator")
        
        # Cancel all worker tasks
        for worker in self.agent_workers.values():
            worker.cancel()
        
        # Wait for workers to complete
        if self.agent_workers:
            await asyncio.gather(*self.agent_workers.values(), return_exceptions=True)
        
        # Clean up
        self.agents.clear()
        self.message_queues.clear()
        self.agent_workers.clear()
        
        logger.info("Agent Coordinator shutdown complete")


# Convenience functions for common operations

async def analyze_property_quick(coordinator: AgentCoordinator, address: str, 
                               listing_price: Optional[float] = None) -> Dict[str, Any]:
    """Quick property analysis through agent coordination"""
    
    request = AgentRequest(
        request_id=str(uuid.uuid4()),
        requesting_agent=AgentType.CUSTOMER_AGENT,
        target_agent=AgentType.ANALYSIS_ENGINE,
        request_type="quick_analysis",
        payload={
            "address": address,
            "listing_price": listing_price
        },
        priority=MessagePriority.NORMAL.value
    )
    
    response = await coordinator.send_and_wait(request)
    
    if response.success:
        return response.payload.get("quick_analysis", {})
    else:
        raise RuntimeError(f"Analysis failed: {response.error_message}")


async def analyze_property_comprehensive(coordinator: AgentCoordinator, address: str,
                                       user_preferences: Optional[Dict[str, Any]] = None) -> PropertyAnalysis:
    """Comprehensive property analysis through agent coordination"""
    
    request = AgentRequest(
        request_id=str(uuid.uuid4()),
        requesting_agent=AgentType.CUSTOMER_AGENT,
        target_agent=AgentType.ANALYSIS_ENGINE,
        request_type="property_analysis",
        payload={
            "address": address,
            "user_preferences": user_preferences or {}
        },
        priority=MessagePriority.HIGH.value
    )
    
    response = await coordinator.send_and_wait(request, timeout_seconds=600)  # 10 minutes for comprehensive
    
    if response.success:
        return response.payload.get("analysis_result", {})
    else:
        raise RuntimeError(f"Comprehensive analysis failed: {response.error_message}")


# Global coordinator instance
_global_coordinator: Optional[AgentCoordinator] = None

def get_agent_coordinator() -> AgentCoordinator:
    """Get or create the global agent coordinator instance"""
    global _global_coordinator
    
    if _global_coordinator is None:
        _global_coordinator = AgentCoordinator()
    
    return _global_coordinator