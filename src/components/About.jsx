import React from 'react';
import usamaPhoto from "../assets/pic.jpg";
import { User, Code, Heart, Globe, Github, Linkedin, Mail } from 'lucide-react';

const About = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-nature-green-50 via-sky-blue-50 to-nature-green-100 p-8">
      <div className="max-w-4xl mx-auto pt-20">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-nature-green-100 rounded-full mb-6">
            <User className="w-8 h-8 text-nature-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            About Me
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Learn more about the developer and the story behind this Green Space Tracker project
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-white/20">
          {/* Profile Section */}
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8 mb-12">
            {/* Profile Picture */}
            <div className="flex-shrink-0">
              <div className="w-48 h-48 rounded-2xl shadow-lg border-4 border-white overflow-hidden bg-gradient-to-br from-nature-green-100 to-sky-blue-100">
                <img 
                  src={usamaPhoto} 
                  alt="Usama Tufail - Developer" 
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback in case image fails to load
                    e.target.style.display = 'none';
                    e.target.parentNode.innerHTML = `
                      <div class="w-full h-full flex items-center justify-center">
                        <div class="text-center">
                          <User class="w-16 h-16 text-nature-green-600 mx-auto mb-2" />
                          <p class="text-sm text-gray-600 font-medium">Usama Tufail</p>
                          <p class="text-xs text-gray-500">Photo Loading...</p>
                        </div>
                      </div>
                    `;
                  }}
                />
              </div>
            </div>

            {/* Personal Information */}
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                Hi, I'm Usama Tufail
              </h2>
              <p className="text-lg text-gray-600 leading-relaxed mb-6">
                I'm a passionate developer committed to creating technology solutions that make a positive impact on our environment and communities. This Green Space Tracker project represents my dedication to combining technical skills with environmental consciousness.
              </p>
              
              {/* Project Information */}
              <div className="bg-gradient-to-r from-nature-green-50 to-sky-blue-50 rounded-xl p-6 border border-nature-green-200 mb-6">
                <div className="flex items-center gap-3 mb-3">
                  <Heart className="w-6 h-6 text-red-500" />
                  <h3 className="text-xl font-semibold text-gray-800">Volunteer Project</h3>
                </div>
                <p className="text-gray-600 leading-relaxed">
                  This was my volunteer project, developed with the goal of helping cities and communities better understand and track their green spaces. I believe that access to green areas is crucial for urban sustainability and quality of life, and technology can play a vital role in monitoring and improving these spaces.
                </p>
              </div>

              {/* Skills & Technologies */}
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Code className="w-5 h-5 text-nature-green-600" />
                  Technologies Used
                </h3>
                <div className="flex flex-wrap gap-2">
                  {['React', 'JavaScript', 'Python', 'FastAPI', 'Tailwind CSS', 'SQLite', 'Geospatial APIs'].map((tech) => (
                    <span 
                      key={tech}
                      className="bg-nature-green-100 text-nature-green-800 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Mission Section */}
          <div className="bg-gradient-to-r from-sky-blue-50 to-nature-green-50 rounded-xl p-6 border border-sky-blue-200 mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Globe className="w-6 h-6 text-sky-blue-600" />
              <h3 className="text-xl font-semibold text-gray-800">Project Mission</h3>
            </div>
            <p className="text-gray-600 leading-relaxed">
              The Green Space Tracker aims to democratize access to urban green space data, helping cities, researchers, and citizens make informed decisions about urban planning and environmental sustainability. By providing easy-to-use tools for tracking parks, green coverage, and environmental data, we can work together towards more livable, sustainable cities.
            </p>
          </div>

          {/* Contact Information */}
          <div className="text-center">
            <h3 className="text-xl font-semibold text-gray-800 mb-6">Let's Connect</h3>
            <div className="flex justify-center gap-4">
              <button className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors duration-200">
                <Github className="w-4 h-4" />
                <span>GitHub</span>
              </button>
              <button className="flex items-center gap-2 bg-blue-100 hover:bg-blue-200 text-blue-700 px-4 py-2 rounded-lg transition-colors duration-200">
                <Linkedin className="w-4 h-4" />
                <span>LinkedIn</span>
              </button>
              <button className="flex items-center gap-2 bg-green-100 hover:bg-green-200 text-green-700 px-4 py-2 rounded-lg transition-colors duration-200">
                <Mail className="w-4 h-4" />
                <span>Email</span>
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-4">
              Feel free to reach out if you'd like to collaborate on environmental tech projects!
            </p>
          </div>
        </div>

        {/* Footer Quote */}
        <div className="text-center mt-12">
          <blockquote className="text-lg italic text-gray-600 max-w-2xl mx-auto">
            "Technology should serve humanity and our planet. Every line of code is an opportunity to make the world a little bit better."
          </blockquote>
          <p className="text-sm text-gray-500 mt-2">- Usama Tufail</p>
        </div>
      </div>
    </div>
  );
};

export default About;