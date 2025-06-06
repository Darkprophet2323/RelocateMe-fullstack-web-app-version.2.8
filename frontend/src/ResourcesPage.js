import React, { useState, useEffect } from "react";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ResourcesPage = () => {
  const [resources, setResources] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [totalResources, setTotalResources] = useState(0);

  useEffect(() => {
    fetchResources();
  }, []);

  const fetchResources = async () => {
    try {
      const response = await axios.get(`${API}/api/resources/all`);
      setResources(response.data);
      
      // Count total resources
      let total = 0;
      Object.values(response.data).forEach(category => {
        total += category.length;
      });
      setTotalResources(total);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching resources:', error);
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults([]);
      setSearching(false);
      return;
    }
    
    setSearching(true);
    
    // Implement client-side search since backend search endpoint might not be available
    const searchResults = [];
    const queryLower = query.toLowerCase();
    
    // Search through all resource categories
    Object.entries(resources).forEach(([categoryKey, categoryResources]) => {
      if (Array.isArray(categoryResources)) {
        categoryResources.forEach((resource) => {
          if (
            resource.name.toLowerCase().includes(queryLower) ||
            resource.description.toLowerCase().includes(queryLower) ||
            resource.url.toLowerCase().includes(queryLower)
          ) {
            searchResults.push({
              ...resource,
              category: categoryKey.replace('_', ' ').toUpperCase()
            });
          }
        });
      }
    });
    
    setSearchResults(searchResults);
    setSearching(false);
  };

  const resetAnalytics = async () => {
    try {
      // Since this needs authentication, show a message about requiring login
      const confirmReset = window.confirm(
        "Reset Analytics: This will clear all progress data. " +
        "Note: This feature requires authentication. " +
        "Continue to attempt reset?"
      );
      
      if (!confirmReset) return;
      
      await axios.post(`${API}/api/analytics/reset`, {}, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      alert("Analytics reset successfully! All progress has been cleared.");
    } catch (error) {
      console.error('Error resetting analytics:', error);
      if (error.response?.status === 401) {
        alert("Analytics reset requires authentication. Please log in first and try again.");
      } else {
        alert("Error resetting analytics: " + (error.response?.data?.detail || error.message));
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 flex items-center justify-center">
        <div className="text-xl text-white font-mono">LOADING RESOURCE DATABASE...</div>
      </div>
    );
  }

  const resourceCategories = [
    { key: 'visa_legal', title: 'VISA & LEGAL', description: 'UK immigration and legal documentation' },
    { key: 'flights_moving', title: 'FLIGHTS & MOVING', description: 'Travel booking and international relocation' },
    { key: 'housing', title: 'HOUSING', description: 'Property search and rental guidance' },
    { key: 'expat_communities', title: 'EXPAT COMMUNITIES', description: 'UK expat networks and support groups' },
    { key: 'healthcare', title: 'HEALTHCARE', description: 'NHS and private healthcare options' },
    { key: 'financial', title: 'FINANCIAL', description: 'Banking and financial services' },
    { key: 'transport_driving', title: 'TRANSPORT & DRIVING', description: 'UK driving licenses and public transport' },
    { key: 'education', title: 'EDUCATION', description: 'Schools and educational opportunities' },
    { key: 'legal_tax', title: 'LEGAL & TAX', description: 'UK tax obligations and legal assistance' },
    { key: 'peak_district_lifestyle', title: 'PEAK DISTRICT LIFESTYLE', description: 'Local attractions and community life' },
    { key: 'miscellaneous', title: 'MISCELLANEOUS', description: 'Additional services and utilities' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6 md:mb-8 fade-in">
          <h1 className="text-3xl md:text-5xl font-bold font-serif text-white mb-4 md:mb-6">
            RESOURCE NETWORK
          </h1>
          <p className="text-lg md:text-xl text-gray-400 mb-6 md:mb-8 font-mono tracking-wide">
            [ {totalResources}+ VERIFIED RESOURCES FOR RELOCATION SUCCESS ]
          </p>
        </div>

        {/* Search Interface */}
        <div className="mb-6 md:mb-8 bg-black border border-gray-600 p-4 md:p-8 hover:border-white transition-all duration-300">
          <h2 className="text-xl md:text-2xl font-bold text-white mb-4 md:mb-6 font-mono tracking-wider">RESOURCE SEARCH</h2>
          <div className="flex flex-col gap-4 mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search resources by name, description, or URL..."
              className="w-full px-4 md:px-6 py-3 md:py-4 bg-black border-2 border-gray-600 text-white font-mono focus:border-white focus:outline-none transition-all duration-300"
            />
            <button
              onClick={() => handleSearch(searchQuery)}
              className="hoverable bg-white text-black px-6 md:px-8 py-3 md:py-4 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300 border-2 border-white"
            >
              [SEARCH]
            </button>
          </div>
          
          {/* Reset Analytics Button */}
          <div className="flex justify-center md:justify-end">
            <button
              onClick={resetAnalytics}
              className="hoverable bg-red-900 text-white px-4 md:px-6 py-2 md:py-3 font-mono font-bold tracking-wider border-2 border-red-700 hover:bg-red-800 transition-all duration-300 text-sm md:text-base"
            >
              [RESET ANALYTICS]
            </button>
          </div>

          {/* Search Results */}
          {searching && (
            <div className="text-center py-6">
              <div className="text-lg text-gray-400 font-mono">SEARCHING DATABASE...</div>
            </div>
          )}
          
          {searchQuery && searchResults.length > 0 && (
            <div className="mt-8">
              <h3 className="text-lg md:text-xl font-bold text-white mb-4 md:mb-6 font-mono">
                SEARCH RESULTS ({searchResults.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {searchResults.map((resource, index) => (
                  <a
                    key={index}
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hoverable bg-gray-900 border border-gray-700 p-4 hover:border-white transition-all duration-300"
                  >
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start mb-2">
                      <h4 className="font-bold text-white text-sm font-mono mb-1 md:mb-0">{resource.name}</h4>
                      <span className="text-xs text-gray-500 font-mono">{resource.category}</span>
                    </div>
                    <p className="text-gray-400 text-xs font-mono">{resource.description}</p>
                  </a>
                ))}
              </div>
            </div>
          )}
          
          {searchQuery && searchResults.length === 0 && !searching && (
            <div className="text-center py-6">
              <div className="text-lg text-gray-400 font-mono">NO RESOURCES FOUND FOR: "{searchQuery}"</div>
            </div>
          )}
        </div>

        {/* Resource Categories */}
        {(!searchQuery || searchResults.length === 0) && (
          <div className="space-y-6 md:space-y-8">
            {resourceCategories.map((category) => {
              const categoryResources = resources[category.key] || [];
              return (
                <div key={category.key} className="bg-black border border-gray-600 p-4 md:p-8 hover:border-white transition-all duration-300">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4 md:mb-6">
                    <div className="mb-4 md:mb-0">
                      <h2 className="text-xl md:text-2xl font-bold text-white font-mono tracking-wider">
                        {category.title}
                      </h2>
                      <p className="text-gray-400 text-sm font-mono mt-2">{category.description}</p>
                    </div>
                    <span className="bg-white text-black px-3 md:px-4 py-1 md:py-2 font-mono font-bold tracking-wider text-sm md:text-base">
                      {categoryResources.length} LINKS
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {categoryResources.map((resource, index) => (
                      <a
                        key={index}
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hoverable bg-gray-900 border border-gray-700 p-4 hover:border-white transition-all duration-300 block"
                      >
                        <h3 className="font-bold text-white mb-2 font-mono tracking-wide text-sm md:text-base">
                          {resource.name}
                        </h3>
                        <p className="text-gray-400 text-xs md:text-sm font-mono mb-2">{resource.description}</p>
                        <div className="text-xs text-gray-500 font-mono break-all">→ {resource.url}</div>
                      </a>
                    ))}
                  </div>
                  
                  {categoryResources.length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-gray-400 font-mono">No resources loaded for this category</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Summary */}
        <div className="mt-8 md:mt-12 bg-black border border-gray-600 p-6 md:p-8 text-center hover:border-white transition-all duration-300">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-4 md:mb-6 font-serif">RESOURCE SUMMARY</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
            <div className="bg-gray-900 border border-gray-700 p-3 md:p-4">
              <div className="text-2xl md:text-3xl font-bold text-white mb-1 md:mb-2 font-mono">{totalResources}+</div>
              <div className="text-gray-400 text-xs md:text-sm font-mono tracking-wider">TOTAL RESOURCES</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-3 md:p-4">
              <div className="text-2xl md:text-3xl font-bold text-white mb-1 md:mb-2 font-mono">{resourceCategories.length}</div>
              <div className="text-gray-400 text-xs md:text-sm font-mono tracking-wider">CATEGORIES</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-3 md:p-4">
              <div className="text-2xl md:text-3xl font-bold text-white mb-1 md:mb-2 font-mono">39</div>
              <div className="text-gray-400 text-xs md:text-sm font-mono tracking-wider">TIMELINE STEPS</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-3 md:p-4">
              <div className="text-2xl md:text-3xl font-bold text-white mb-1 md:mb-2 font-mono">100%</div>
              <div className="text-gray-400 text-xs md:text-sm font-mono tracking-wider">VERIFIED</div>
            </div>
          </div>
          <p className="text-gray-300 font-mono leading-relaxed text-sm md:text-base">
            Complete resource database for Phoenix to Peak District relocation. All links verified and 
            categorized for efficient access during your emigration journey.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResourcesPage;