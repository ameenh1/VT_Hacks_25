import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import logo from '@/assets/logo.jpg';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Marketplace', path: '/marketplace' },
    { name: 'Analyzer', path: '/analyzer' },
    { name: 'Agent Connect', path: '/agent-connect' },
    { name: 'Pricing', path: '/pricing' },
  ];

  return (
    <nav className="border-b border-border/50 bg-white/80 backdrop-blur-xl sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <img src={logo} alt="EquityAI" className="h-10 w-10 rounded-lg shadow-sm group-hover:shadow-md transition-shadow" />
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-emerald-500/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </div>
            <span className="font-bold text-2xl text-foreground group-hover:text-primary transition-colors">EquityAI</span>
          </Link>

          {/* Center Navigation */}
          <div className="hidden md:flex space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                  location.pathname === item.path
                    ? 'text-primary bg-primary/10 shadow-sm'
                    : 'text-foreground hover:text-primary hover:bg-primary/5'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-3">
            <Link to="/signin">
              <Button variant="ghost" size="sm" className="hover:bg-primary/5 hover:text-primary transition-colors">
                Sign In
              </Button>
            </Link>
            <Link to="/signup">
              <Button size="sm" className="bg-gradient-to-r from-primary to-emerald-600 text-primary-foreground hover:from-primary/90 hover:to-emerald-600/90 shadow-sm hover:shadow-md transition-all duration-200">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;