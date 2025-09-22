import React from 'react';

const Footer = () => {
  // Eco-friendly SVG icons
  const LeafIcon = () => (
    <svg className="w-6 h-6 text-green-300" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
    </svg>
  );

  const TreeIcon = () => (
    <svg className="w-6 h-6 text-green-300" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2l3.09 6.26L22 9l-5 4.87L18.18 22 12 18.27 5.82 22 7 13.87 2 9l6.91-.74L12 2z"/>
      <path d="M12 2C8.69 2 6 4.69 6 8c0 2.76 1.86 5.09 4.4 5.78L8.5 16h3v5.5c0 .28.22.5.5.5s.5-.22.5-.5V16h3l-1.9-2.22C16.14 13.09 18 10.76 18 8c0-3.31-2.69-6-6-6z"/>
    </svg>
  );

  const RecycleIcon = () => (
    <svg className="w-6 h-6 text-green-300" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM8 17.5c-1.38 0-2.5-1.12-2.5-2.5 0-.61.22-1.17.59-1.61L12 7.5l5.91 5.89c.37.44.59 1 .59 1.61 0 1.38-1.12 2.5-2.5 2.5H8z"/>
    </svg>
  );

  return (
    <footer className="bg-green-600 text-white py-12 px-4 mt-16">
      <div className="max-w-6xl mx-auto">
        {/* Main grid layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
          
          {/* Left Section - Eco Icons */}
          <div className="flex justify-center md:justify-start space-x-6">
            <div className="flex flex-col items-center group cursor-pointer">
              <LeafIcon />
              <span className="text-xs mt-1 opacity-75 group-hover:opacity-100 transition-opacity">
                Green
              </span>
            </div>
            <div className="flex flex-col items-center group cursor-pointer">
              <TreeIcon />
              <span className="text-xs mt-1 opacity-75 group-hover:opacity-100 transition-opacity">
                Nature
              </span>
            </div>
            <div className="flex flex-col items-center group cursor-pointer">
              <RecycleIcon />
              <span className="text-xs mt-1 opacity-75 group-hover:opacity-100 transition-opacity">
                Sustainable
              </span>
            </div>
          </div>

          {/* Center Section - Call to Action */}
          <div className="text-center">
            <h3 className="text-xl md:text-2xl font-bold text-green-100 mb-2">
              Let's make our cities greener together
            </h3>
            <p className="text-green-200 text-sm">
              Building sustainable urban environments for future generations
            </p>
          </div>

          {/* Right Section - Navigation Links */}
          <div className="flex justify-center md:justify-end">
            <nav className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-6">
              <a 
                href="#contact" 
                className="text-white hover:text-green-200 transition-colors duration-300 font-medium"
              >
                Contact
              </a>
              <a 
                href="#privacy" 
                className="text-white hover:text-green-200 transition-colors duration-300 font-medium"
              >
                Privacy
              </a>
              <a 
                href="#about" 
                className="text-white hover:text-green-200 transition-colors duration-300 font-medium"
              >
                About
              </a>
            </nav>
          </div>
        </div>

        {/* Bottom Section - Copyright */}
        <div className="border-t border-green-500 mt-8 pt-6 text-center">
          <p className="text-green-200 text-sm">
            © {new Date().getFullYear()} Urban Green Initiative. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;