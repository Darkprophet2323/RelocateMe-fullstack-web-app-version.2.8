// Employment Page with Job Filtering and Comprehensive Content
const EmploymentPage = () => {
  const [jobsData, setJobsData] = useState({ jobs: [], categories: [], job_types: [] });
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [filters, setFilters] = useState({
    category: 'all',
    job_type: 'all',
    search: ''
  });

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await axios.get(`${API}/api/jobs/listings`);
        setJobsData(response.data);
        setFilteredJobs(response.data.jobs);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      }
    };
    fetchJobs();
  }, []);

  useEffect(() => {
    let filtered = jobsData.jobs;

    if (filters.category !== 'all') {
      filtered = filtered.filter(job => job.category === filters.category);
    }

    if (filters.job_type !== 'all') {
      filtered = filtered.filter(job => job.job_type === filters.job_type);
    }

    if (filters.search) {
      filtered = filtered.filter(job => 
        job.title.toLowerCase().includes(filters.search.toLowerCase()) ||
        job.company.toLowerCase().includes(filters.search.toLowerCase()) ||
        job.location.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    setFilteredJobs(filtered);
  }, [filters, jobsData]);

  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const employmentLinks = [
    { name: "Indeed UK", url: "https://uk.indeed.com", description: "UK's largest job search platform" },
    { name: "Reed", url: "https://www.reed.co.uk", description: "Leading UK recruitment website" },
    { name: "LinkedIn UK", url: "https://www.linkedin.com/jobs", description: "Professional networking and jobs" },
    { name: "Peak District Jobs", url: "https://www.peakdistrictjobs.co.uk", description: "Local job opportunities in the region" },
    { name: "CV Templates", url: "https://www.gov.uk/cv-tips", description: "UK-specific CV writing guidance" },
    { name: "Work Permits", url: "https://www.gov.uk/browse/working", description: "Working in the UK information" },
    { name: "Salary Benchmarking", url: "https://www.glassdoor.co.uk", description: "Compare salaries and companies" },
    { name: "Career Guidance", url: "https://nationalcareers.service.gov.uk", description: "National careers service" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            💼 Peak District Job Opportunities
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Discover {jobsData.jobs.length} real job opportunities in your new home region
          </p>
        </div>

        {/* Employment Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🔍 Job Search Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {employmentLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white rounded-xl shadow-lg p-4 hover:shadow-xl transition-all duration-300"
              >
                <h3 className="font-bold text-blue-600 mb-2">{link.name}</h3>
                <p className="text-gray-600 text-sm">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🔍 Filter Jobs</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <input
                type="text"
                placeholder="Job title, company, location..."
                value={filters.search}
                onChange={(e) => updateFilter('search', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={filters.category}
                onChange={(e) => updateFilter('category', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Categories</option>
                {jobsData.categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Job Type</label>
              <select
                value={filters.job_type}
                onChange={(e) => updateFilter('job_type', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Types</option>
                {jobsData.job_types.map(type => (
                  <option key={type} value={type}>{type.replace('-', ' ').toUpperCase()}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ category: 'all', job_type: 'all', search: '' })}
                className="w-full bg-gray-600 text-white px-4 py-3 rounded-lg hover:bg-gray-700 transition duration-300 font-medium"
              >
                🔄 Reset Filters
              </button>
            </div>
          </div>
          <div className="mt-4 text-center">
            <span className="text-gray-600">
              Showing {filteredJobs.length} of {jobsData.jobs.length} jobs
            </span>
          </div>
        </div>

        {/* Job Listings */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredJobs.map(job => (
            <div key={job.id} className="bg-white rounded-xl shadow-lg p-6 transition-all duration-300 hover:shadow-xl hover:scale-102">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{job.title}</h3>
                  <p className="text-lg text-blue-600 font-semibold">{job.company}</p>
                  <p className="text-gray-600">📍 {job.location}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">{job.salary}</div>
                  <div className="text-sm text-gray-500">{job.job_type.replace('-', ' ')}</div>
                </div>
              </div>

              <p className="text-gray-700 mb-4 leading-relaxed">{job.description}</p>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {job.category}
                </span>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  {job.job_type.replace('-', ' ')}
                </span>
                {job.remote_work && (
                  <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                    🏠 Remote Available
                  </span>
                )}
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold text-gray-900 mb-2">Key Requirements:</h4>
                <ul className="text-sm text-gray-600 space-y-1 mb-4">
                  {job.requirements.slice(0, 3).map((req, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      {req}
                    </li>
                  ))}
                  {job.requirements.length > 3 && (
                    <li className="text-gray-500 italic">
                      +{job.requirements.length - 3} more requirements
                    </li>
                  )}
                </ul>

                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-500">
                    Posted: {new Date(job.posted_date).toLocaleDateString()}
                  </div>
                  <a
                    href={job.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition duration-300 font-medium"
                  >
                    Apply Now →
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredJobs.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No Jobs Found</h2>
            <p className="text-gray-600">Try adjusting your search criteria or browse all available positions.</p>
            <button
              onClick={() => setFilters({ category: 'all', job_type: 'all', search: '' })}
              className="mt-4 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition duration-300 font-medium"
            >
              🔄 Show All Jobs
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Comprehensive Housing Page
const HousingPage = () => {
  const [selectedTab, setSelectedTab] = useState('comparison');

  const housingLinks = [
    { name: "Rightmove", url: "https://www.rightmove.co.uk", description: "UK's largest property portal" },
    { name: "Zoopla", url: "https://www.zoopla.co.uk", description: "Property search and valuation" },
    { name: "SpareRoom", url: "https://www.spareroom.co.uk", description: "Room rental and flatshare platform" },
    { name: "Peak District Property", url: "https://www.peakdistrictproperty.co.uk", description: "Local estate agents" },
    { name: "Council Tax Calculator", url: "https://www.gov.uk/council-tax", description: "Calculate council tax rates" },
    { name: "Utility Setup", url: "https://www.ofgem.gov.uk", description: "Energy regulator and supplier info" },
    { name: "Broadband Comparison", url: "https://www.ofcom.org.uk/phones-telecoms-and-internet/advice-for-consumers/broadband-speeds", description: "Compare internet providers" },
    { name: "Home Insurance", url: "https://www.comparethemarket.com/home-insurance/", description: "Compare home insurance" }
  ];

  const comparison = {
    phoenix: {
      name: "Phoenix, Arizona",
      median_price: "$445,000",
      rental_price: "$1,400/month",
      property_tax: "0.6% annually",
      utilities: "$120/month",
      climate: "Desert, hot summers",
      population: "1.7 million",
      pros: ["Warm weather year-round", "Lower cost of living", "No state income tax", "Growing tech sector"],
      cons: ["Extreme summer heat", "Water scarcity concerns", "Urban sprawl", "Limited public transport"]
    },
    peak_district: {
      name: "Peak District, UK",
      median_price: "£285,000",
      rental_price: "£950/month",
      property_tax: "Council Tax varies",
      utilities: "£150/month",
      climate: "Temperate, mild summers",
      population: "38,000 residents",
      pros: ["Stunning natural beauty", "Rich history and culture", "Strong community", "Excellent hiking/outdoor activities"],
      cons: ["Higher living costs", "Limited job market", "Weather can be unpredictable", "Rural location"]
    }
  };

  const propertyTypes = [
    { 
      type: "Traditional Stone Cottage", 
      price: "£200,000 - £400,000", 
      description: "Characteristic Peak District homes with original features",
      features: ["Stone construction", "Original beams", "Open fireplaces", "Garden/outdoor space"]
    },
    { 
      type: "Modern Family Home", 
      price: "£350,000 - £600,000", 
      description: "Contemporary builds with modern amenities",
      features: ["Energy efficient", "Modern kitchen", "Multiple bedrooms", "Parking"]
    },
    { 
      type: "Village Terraced House", 
      price: "£180,000 - £320,000", 
      description: "Traditional terraced homes in village centers",
      features: ["Period features", "Village location", "Walking distance to amenities", "Character property"]
    },
    { 
      type: "Rural Farmhouse", 
      price: "£400,000 - £800,000", 
      description: "Converted farmhouses with substantial grounds",
      features: ["Large plot", "Outbuildings", "Privacy", "Rural views"]
    }
  ];

  const schoolsAndAmenities = [
    { name: "Peak District Primary Schools", rating: "Outstanding", description: "Excellent local primary education" },
    { name: "Lady Manners School", rating: "Good", description: "Secondary school in Bakewell" },
    { name: "Bakewell Medical Centre", rating: "4.5/5", description: "Main healthcare facility" },
    { name: "Local Shopping", rating: "Good", description: "Village shops and weekly markets" },
    { name: "Transport Links", rating: "Moderate", description: "Bus services to major cities" },
    { name: "Recreation", rating: "Excellent", description: "Hiking, cycling, outdoor activities" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            🏘️ Housing Guide: Phoenix vs Peak District
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Comprehensive comparison and guidance for your housing search
          </p>
        </div>

        {/* Housing Resources */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🏠 Housing & Property Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {housingLinks.map((link, index) => (
              <a
                key={index}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white rounded-xl shadow-lg p-4 hover:shadow-xl transition-all duration-300"
              >
                <h3 className="font-bold text-blue-600 mb-2">{link.name}</h3>
                <p className="text-gray-600 text-sm">{link.description}</p>
              </a>
            ))}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setSelectedTab('comparison')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                selectedTab === 'comparison'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              📊 Location Comparison
            </button>
            <button
              onClick={() => setSelectedTab('properties')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                selectedTab === 'properties'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              🏡 Property Types
            </button>
            <button
              onClick={() => setSelectedTab('amenities')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                selectedTab === 'amenities'
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              🎯 Schools & Amenities
            </button>
          </div>
        </div>

        {/* Location Comparison */}
        {selectedTab === 'comparison' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {Object.entries(comparison).map(([key, location]) => (
              <div key={key} className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">{location.name}</h2>
                
                <div className="space-y-4 mb-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Median Home Price</div>
                      <div className="text-lg font-bold text-blue-600">{location.median_price}</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Rental Price</div>
                      <div className="text-lg font-bold text-green-600">{location.rental_price}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-purple-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Property Tax</div>
                      <div className="text-sm font-medium">{location.property_tax}</div>
                    </div>
                    <div className="bg-yellow-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Utilities</div>
                      <div className="text-sm font-medium">{location.utilities}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Climate</div>
                      <div className="text-sm font-medium">{location.climate}</div>
                    </div>
                    <div className="bg-indigo-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Population</div>
                      <div className="text-sm font-medium">{location.population}</div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-green-700 mb-2">✅ Pros</h3>
                    <ul className="space-y-1">
                      {location.pros.map((pro, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-start">
                          <span className="text-green-500 mr-2">+</span>
                          {pro}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-red-700 mb-2">⚠️ Cons</h3>
                    <ul className="space-y-1">
                      {location.cons.map((con, index) => (
                        <li key={index} className="text-sm text-gray-600 flex items-start">
                          <span className="text-red-500 mr-2">-</span>
                          {con}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Property Types */}
        {selectedTab === 'properties' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {propertyTypes.map((property, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-2">{property.type}</h3>
                <div className="text-2xl font-bold text-blue-600 mb-3">{property.price}</div>
                <p className="text-gray-600 mb-4">{property.description}</p>
                
                <h4 className="font-semibold text-gray-900 mb-2">Key Features:</h4>
                <ul className="space-y-1">
                  {property.features.map((feature, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {/* Schools & Amenities */}
        {selectedTab === 'amenities' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schoolsAndAmenities.map((amenity, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-2">{amenity.name}</h3>
                <div className="flex items-center mb-3">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {amenity.rating}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">{amenity.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
