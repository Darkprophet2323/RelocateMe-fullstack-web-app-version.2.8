import React, { useState, useEffect } from "react";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const JobsPage = () => {
  const [jobs, setJobs] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [filterType, setFilterType] = useState("all");

  useEffect(() => {
    fetchJobsAndPlatforms();
  }, []);

  useEffect(() => {
    filterJobs();
  }, [searchQuery, filterType, jobs]);

  const fetchJobsAndPlatforms = async () => {
    try {
      console.log('Fetching jobs and platforms...');
      
      // Fetch both jobs and platforms
      const [jobsResponse, platformsResponse] = await Promise.all([
        axios.get(`${API}/api/jobs/hospitality`),
        axios.get(`${API}/api/jobs/search-platforms`)
      ]);
      
      console.log('Jobs response:', jobsResponse.data);
      console.log('Platforms response:', platformsResponse.data);
      
      if (jobsResponse.data && jobsResponse.data.featured_jobs) {
        setJobs(jobsResponse.data.featured_jobs);
        setFilteredJobs(jobsResponse.data.featured_jobs);
      } else {
        setFallbackJobs();
      }

      if (platformsResponse.data && platformsResponse.data.platforms) {
        setPlatforms(platformsResponse.data.platforms.slice(0, 4)); // Show only first 4
      } else {
        setFallbackPlatforms();
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      console.log('API calls failed, using fallback data');
      setFallbackJobs();
      setFallbackPlatforms();
      setLoading(false);
    }
  };

  const setFallbackPlatforms = () => {
    const fallbackPlatforms = [
      {
        "name": "AI Apply",
        "url": "https://aiapply.co",
        "description": "AI-powered job application platform",
        "icon": "🤖"
      },
      {
        "name": "Indeed UK",
        "url": "https://uk.indeed.com/jobs?q=hospitality&l=Peak+District",
        "description": "Largest UK job search platform",
        "icon": "🔍"
      },
      {
        "name": "Caterer.com",
        "url": "https://www.caterer.com/jobs",
        "description": "Hospitality industry specialists",
        "icon": "🍽️"
      },
      {
        "name": "Leisure Jobs",
        "url": "https://www.leisurejobs.com",
        "description": "Tourism & hospitality careers",
        "icon": "🏨"
      }
    ];
    
    setPlatforms(fallbackPlatforms);
    console.log('Fallback platforms set, total:', fallbackPlatforms.length);
  };

  const setFallbackJobs = () => {
    const fallbackData = [
      {
        "id": 1,
        "title": "Hotel Receptionist - Peak District Resort",
        "company": "Chatsworth Estate Hotels",
        "location": "Bakewell, Peak District",
        "salary": "£22,000 - £26,000 + Tips",
        "type": "Full-time",
        "visa_support": true,
        "remote_options": "Hybrid training available",
        "benefits": [
          "Tier 2 Skilled Worker Visa Sponsorship",
          "On-site accommodation available",
          "Staff meals and uniform provided",
          "28 days holiday + bank holidays"
        ],
        "description": "Join our luxury resort in the heart of Peak District! Perfect for hospitality professionals seeking UK visa sponsorship.",
        "apply_url": "https://www.chatsworth.org/careers",
        "featured": true
      },
      {
        "id": 2,
        "title": "Restaurant Server - Michelin Recommended",
        "company": "The Peacock at Rowsley",
        "location": "Rowsley, Peak District",
        "salary": "£11.50/hour + £200-400 weekly tips",
        "type": "Full-time",
        "visa_support": true,
        "remote_options": "Online training modules",
        "benefits": [
          "Skilled Worker Visa sponsorship available",
          "Share of tips (£200-400/week average)",
          "Staff discount on food and accommodation",
          "Professional development opportunities"
        ],
        "description": "Work in a prestigious Michelin-recommended restaurant with stunning Peak District views.",
        "apply_url": "https://www.thepeacockatrowsley.com/careers",
        "featured": true
      }
    ];
    
    setJobs(fallbackData);
    setFilteredJobs(fallbackData);
    console.log('Fallback jobs set, total:', fallbackData.length);
  };

  const filterJobs = () => {
    let filtered = jobs;

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(query) ||
        job.company.toLowerCase().includes(query) ||
        job.location.toLowerCase().includes(query) ||
        job.description.toLowerCase().includes(query)
      );
    }

    // Filter by type
    if (filterType !== "all") {
      switch (filterType) {
        case "visa":
          filtered = filtered.filter(job => job.visa_support);
          break;
        case "remote":
          filtered = filtered.filter(job => job.remote_options && job.remote_options.toLowerCase().includes("remote"));
          break;
        case "accommodation":
          filtered = filtered.filter(job => 
            job.benefits.some(benefit => 
              benefit.toLowerCase().includes("accommodation") || 
              benefit.toLowerCase().includes("housing")
            )
          );
          break;
        default:
          break;
      }
    }

    setFilteredJobs(filtered);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 flex items-center justify-center">
        <div className="text-xl text-white font-mono">LOADING HOSPITALITY JOBS...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 p-4 md:p-6 no-overflow">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6 md:mb-8 fade-in">
          <h1 className="text-3xl md:text-5xl font-bold font-serif text-white mb-4 md:mb-6">
            HOSPITALITY CAREERS
          </h1>
          <p className="text-lg md:text-xl text-gray-400 mb-6 md:mb-8 font-mono tracking-wide">
            [ PEAK DISTRICT OPPORTUNITIES WITH VISA SPONSORSHIP ]
          </p>
        </div>

        {/* Job Search Sites */}
        <div className="mb-6 md:mb-8 bg-black border border-gray-600 p-4 md:p-8 hover:border-white transition-all duration-300">
          <h2 className="text-xl md:text-2xl font-bold text-white mb-4 md:mb-6 font-mono tracking-wider text-center">
            EXTERNAL JOB SEARCH PLATFORMS
          </h2>
          <p className="text-gray-400 font-mono text-center mb-6">
            Find additional hospitality and tourism opportunities on these specialized job platforms
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {platforms.map((platform, index) => (
              <a
                key={index}
                href={platform.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hoverable bg-gray-900 border border-gray-700 p-4 hover:border-white transition-all duration-300 text-center group no-overflow"
              >
                <div className="text-2xl mb-2">{platform.icon}</div>
                <h3 className="font-bold text-white mb-2 font-mono text-sm break-words">{platform.name}</h3>
                <p className="text-gray-400 text-xs font-mono break-words">{platform.description}</p>
                <div className="text-xs text-gray-500 mt-2 font-mono resource-url">→ {platform.url.replace('https://', '').split('/')[0]}</div>
              </a>
            ))}
          </div>
          
          <div className="text-center mt-6">
            <p className="text-gray-500 font-mono text-xs">
              These platforms specialize in hospitality, tourism, and travel industry positions with visa sponsorship options
            </p>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="mb-6 md:mb-8 bg-black border border-gray-600 p-4 md:p-8 hover:border-white transition-all duration-300">
          <h2 className="text-xl md:text-2xl font-bold text-white mb-4 md:mb-6 font-mono tracking-wider">JOB SEARCH</h2>
          
          <div className="flex flex-col gap-4 mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search jobs by title, company, or location..."
              className="w-full px-4 md:px-6 py-3 md:py-4 bg-black border-2 border-gray-600 text-white font-mono focus:border-white focus:outline-none transition-all duration-300"
            />
            
            <div className="flex flex-col md:flex-row gap-4">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="flex-1 px-4 md:px-6 py-3 md:py-4 bg-black border-2 border-gray-600 text-white font-mono focus:border-white focus:outline-none transition-all duration-300"
              >
                <option value="all">All Jobs</option>
                <option value="visa">Visa Sponsorship Available</option>
                <option value="remote">Remote Options</option>
                <option value="accommodation">Accommodation Included</option>
              </select>
              
              <button
                onClick={() => {setSearchQuery(""); setFilterType("all");}}
                className="hoverable bg-white text-black px-6 md:px-8 py-3 md:py-4 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300 border-2 border-white"
              >
                [CLEAR FILTERS]
              </button>
            </div>
          </div>

          <div className="text-center">
            <p className="text-gray-400 font-mono">
              Showing {filteredJobs.length} of {jobs.length} available positions
            </p>
          </div>
        </div>

        {/* Jobs Listing */}
        <div className="space-y-6 md:space-y-8">
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => (
              <div key={job.id} className="bg-black border border-gray-600 p-6 md:p-8 hover:border-white transition-all duration-300 no-overflow">
                <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start mb-4">
                  <div className="flex-1 mb-4 lg:mb-0">
                    <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                      <h2 className="text-2xl md:text-3xl font-bold text-white font-mono tracking-wide break-words">
                        {job.title}
                      </h2>
                      {job.featured && (
                        <span className="bg-yellow-600 text-black px-3 py-1 text-xs font-mono font-bold tracking-wider w-fit">
                          FEATURED
                        </span>
                      )}
                    </div>
                    
                    <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 text-gray-400 font-mono mb-4">
                      <span>🏢 {job.company}</span>
                      <span>📍 {job.location}</span>
                      <span>💰 {job.salary}</span>
                      <span className="text-green-400">⏰ {job.type}</span>
                    </div>

                    <p className="text-gray-300 font-mono leading-relaxed mb-4 break-words">
                      {job.description}
                    </p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.visa_support && (
                        <span className="bg-green-900 text-white px-3 py-1 text-xs font-mono border border-green-700">
                          🛂 VISA SPONSORSHIP
                        </span>
                      )}
                      {job.remote_options && (
                        <span className="bg-blue-900 text-white px-3 py-1 text-xs font-mono border border-blue-700">
                          💻 {job.remote_options}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="lg:ml-8 lg:text-right">
                    <a
                      href={job.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hoverable bg-white text-black px-6 md:px-8 py-3 md:py-4 font-mono font-bold tracking-wider hover:bg-gray-200 transition-all duration-300 border-2 border-white inline-block w-full lg:w-auto text-center"
                    >
                      [APPLY NOW]
                    </a>
                  </div>
                </div>

                {/* Benefits */}
                {job.benefits && job.benefits.length > 0 && (
                  <div className="border-t border-gray-700 pt-4">
                    <h3 className="text-lg font-bold text-white mb-3 font-mono">BENEFITS & PERKS:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {job.benefits.map((benefit, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <span className="text-green-400 font-mono">✓</span>
                          <span className="text-gray-300 font-mono text-sm break-words">{benefit}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="bg-black border border-gray-600 p-8 text-center">
              <h2 className="text-2xl font-bold text-white mb-4 font-mono">NO JOBS FOUND</h2>
              <p className="text-gray-400 font-mono">
                No jobs match your current search criteria. Try adjusting your filters or search terms.
              </p>
            </div>
          )}
        </div>

        {/* Call to Action */}
        <div className="mt-8 md:mt-12 bg-black border border-gray-600 p-6 md:p-8 text-center hover:border-white transition-all duration-300">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-4 md:mb-6 font-serif">START YOUR UK CAREER TODAY</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
            <div className="bg-gray-900 border border-gray-700 p-4">
              <div className="text-2xl md:text-3xl font-bold text-white mb-1 md:mb-2 font-mono">{jobs.filter(job => job.visa_support).length}</div>
              <div className="text-gray-400 text-xs md:text-sm font-mono tracking-wider">VISA SPONSORSHIP JOBS</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-4">
              <div className="text-2xl md:text-3xl font-bold text-white mb-1 md:mb-2 font-mono">{jobs.filter(job => job.remote_options && job.remote_options.toLowerCase().includes("remote")).length}</div>
              <div className="text-gray-400 text-xs md:text-sm font-mono tracking-wider">REMOTE OPPORTUNITIES</div>
            </div>
            <div className="bg-gray-900 border border-gray-700 p-4">
              <div className="text-2xl md:text-3xl font-bold text-white mb-1 md:mb-2 font-mono">{jobs.filter(job => job.benefits.some(benefit => benefit.toLowerCase().includes("accommodation"))).length}</div>
              <div className="text-gray-400 text-xs md:text-sm font-mono tracking-wider">WITH ACCOMMODATION</div>
            </div>
          </div>
          <p className="text-gray-300 font-mono leading-relaxed text-sm md:text-base">
            All positions offer competitive salaries, comprehensive benefits, and genuine opportunities for career advancement 
            in the beautiful Peak District. Visa sponsorship available for qualified international candidates.
          </p>
        </div>
      </div>
    </div>
  );
};

export default JobsPage;