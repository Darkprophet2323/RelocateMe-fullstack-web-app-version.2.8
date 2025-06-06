from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import motor.motor_asyncio
import os
import uuid
from pydantic import BaseModel

# CORS and Security Configuration
app = FastAPI(title="RelocateMe API", description="Phoenix to Peak District Relocation Platform", version="2.6.0")

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://2cdbcfb0-eea9-4326-9b19-b06d91ee205b.preview.emergentagent.com",
    "https://*.emergentagent.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB Connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.relocateme

# Create API router with the /api prefix
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Add a simple root endpoint
@api_router.get("/")
async def root():
    return {"message": "RelocateMe API v2.8", "status": "operational"}

# Models
class User(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    hashed_password: str
    current_step: int = 1
    completed_steps: List[int] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PasswordReset(BaseModel):
    username: str

class PasswordResetComplete(BaseModel):
    username: str
    reset_code: str
    new_password: str

class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    salary_range: str
    job_type: str  # full-time, part-time, contract, remote
    category: str
    description: str
    requirements: List[str]
    benefits: List[str]
    posted_date: str
    application_url: str
    contact_email: Optional[str] = None

class VisaRequirement(BaseModel):
    visa_type: str
    title: str
    description: str
    required_documents: List[str]
    processing_time: str
    fee: str
    eligibility: List[str]
    application_process: List[str]

class TimelineProgressUpdate(BaseModel):
    step_id: int
    completed: bool
    notes: Optional[str] = None

class ProgressItem(BaseModel):
    id: str
    title: str
    description: str
    status: str  # pending, in_progress, completed, blocked
    category: str
    subtasks: List[Dict[str, Any]] = []
    notes: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetAnalysis(BaseModel):
    total_budget: float = 400000.0  # $400k default budget
    moving_costs: float = 25000.0
    visa_fees: float = 5000.0
    initial_housing: float = 50000.0
    living_expenses: float = 75000.0
    emergency_fund: float = 50000.0
    remaining_budget: float = 195000.0

# Enhanced Sample Jobs - Focus on Hospitality/Waitressing
SAMPLE_JOBS = [
    {
        "id": "pd001",
        "title": "Restaurant Manager - Peak District",
        "company": "The Peacock at Rowsley",
        "location": "Rowsley, Peak District",
        "salary_range": "£28,000 - £35,000",
        "job_type": "full-time",
        "category": "Hospitality Management",
        "description": "Lead our award-winning restaurant team in the beautiful Peak District. Perfect for experienced hospitality professionals seeking a management role in stunning surroundings.",
        "requirements": ["5+ years restaurant management", "UK hospitality experience preferred", "Strong leadership skills", "Customer service excellence"],
        "benefits": ["Staff accommodation available", "Training programs", "Career development", "Peak District location"],
        "posted_date": "2025-01-15",
        "application_url": "https://www.peakdistrictjobs.co.uk/restaurant-manager",
        "contact_email": "careers@peacockrowsley.co.uk"
    },
    {
        "id": "pd002", 
        "title": "Senior Waitress/Waiter - Fine Dining",
        "company": "Chatsworth House Restaurant",
        "location": "Chatsworth, Peak District",
        "salary_range": "£22,000 - £26,000 + tips",
        "job_type": "full-time",
        "category": "Hospitality Service",
        "description": "Join our prestigious fine dining team at historic Chatsworth House. Excellent opportunity for experienced waitressing professionals.",
        "requirements": ["2+ years fine dining experience", "Excellent English", "Professional presentation", "Wine knowledge preferred"],
        "benefits": ["Historic location", "Staff discounts", "Training provided", "Tips averaging £150/week"],
        "posted_date": "2025-01-20",
        "application_url": "https://www.chatsworth.org/careers",
        "contact_email": "hospitality@chatsworth.org"
    },
    {
        "id": "pd003",
        "title": "Head Waitress - Country Pub",
        "company": "The Old Nag's Head",
        "location": "Edale, Peak District", 
        "salary_range": "£24,000 - £28,000",
        "job_type": "full-time",
        "category": "Hospitality Service",
        "description": "Lead waitressing position in traditional Peak District pub. Perfect for professionals wanting authentic British hospitality experience.",
        "requirements": ["3+ years waitressing", "Supervisory experience", "Beer/spirits knowledge", "Friendly personality"],
        "benefits": ["Staff accommodation nearby", "Meals included", "Beautiful location", "Close-knit team"],
        "posted_date": "2025-01-18",
        "application_url": "https://www.oldnagshead.co.uk/jobs",
        "contact_email": "jobs@oldnagshead.co.uk"
    },
    {
        "id": "pd004",
        "title": "Catering Assistant - Hotel",
        "company": "The Cavendish Hotel",
        "location": "Baslow, Peak District",
        "salary_range": "£20,000 - £23,000",
        "job_type": "full-time", 
        "category": "Hospitality Support",
        "description": "Support role in luxury hotel restaurant and events. Great entry point for hospitality career in Peak District.",
        "requirements": ["Food safety certificate", "Team player", "Flexible hours", "Customer focus"],
        "benefits": ["Training opportunities", "Career progression", "Staff rates", "Beautiful setting"],
        "posted_date": "2025-01-22",
        "application_url": "https://www.cavendish-hotel.net/careers",
        "contact_email": "hr@cavendish-hotel.net"
    },
    {
        "id": "pd005",
        "title": "Cafe Manager/Waitress",
        "company": "Peak District Tea Rooms",
        "location": "Bakewell, Peak District",
        "salary_range": "£25,000 - £30,000",
        "job_type": "full-time",
        "category": "Hospitality Management", 
        "description": "Manage charming tea rooms in the heart of Bakewell. Combine management duties with hands-on service.",
        "requirements": ["Cafe/restaurant management", "Waitressing skills", "Local knowledge helpful", "Business acumen"],
        "benefits": ["Management experience", "Local community", "Flexible approach", "Growth potential"],
        "posted_date": "2025-01-25",
        "application_url": "https://www.peakdistricttearooms.co.uk/jobs",
        "contact_email": "manager@pdtearooms.co.uk"
    },
    {
        "id": "pd006",
        "title": "Event Waitress - Weddings & Functions",
        "company": "Peak District Event Services",
        "location": "Various Peak District Venues",
        "salary_range": "£18,000 - £22,000 + event bonuses",
        "job_type": "full-time",
        "category": "Hospitality Events",
        "description": "Specialist waitressing for weddings and events across Peak District venues. Exciting variety and excellent tips.",
        "requirements": ["Event experience", "Transport essential", "Weekend availability", "Professional appearance"],
        "benefits": ["Varied venues", "Event bonuses", "Flexible scheduling", "Networking opportunities"],
        "posted_date": "2025-01-28",
        "application_url": "https://www.pdevents.co.uk/careers",
        "contact_email": "events@pdevents.co.uk"
    },
    {
        "id": "pd007",
        "title": "Restaurant Supervisor",
        "company": "The Devonshire Arms",
        "location": "Beeley, Peak District",
        "salary_range": "£26,000 - £32,000",
        "job_type": "full-time",
        "category": "Hospitality Management",
        "description": "Supervise restaurant operations in prestigious gastropub. Leadership role with excellent progression opportunities.",
        "requirements": ["Supervisory experience", "Hospitality qualifications", "Wine knowledge", "Leadership skills"],
        "benefits": ["Career development", "Staff accommodation options", "Training budget", "Prestigious employer"],
        "posted_date": "2025-01-30",
        "application_url": "https://www.devonshirearms.co.uk/careers",
        "contact_email": "careers@devonshirearms.co.uk"
    },
    {
        "id": "pd008",
        "title": "Waitress - Tourist Information Centre Cafe",
        "company": "Peak District National Park",
        "location": "Castleton, Peak District",
        "salary_range": "£19,000 - £22,000",
        "job_type": "full-time",
        "category": "Hospitality Tourism",
        "description": "Serve visitors in our information centre cafe. Great way to learn about Peak District while building hospitality career.",
        "requirements": ["Customer service skills", "Tourist knowledge helpful", "Friendly manner", "Team player"],
        "benefits": ["Learning opportunities", "Tourist interaction", "Stable hours", "National Park benefits"],
        "posted_date": "2025-02-01",
        "application_url": "https://www.peakdistrict.gov.uk/jobs",
        "contact_email": "jobs@peakdistrict.gov.uk"
    }
]

# Visa requirements data
VISA_REQUIREMENTS = [
    {
        "visa_type": "Skilled Worker Visa",
        "title": "For Employment-Based Immigration",
        "description": "Most common route for US citizens with job offers. Allows you to work for an approved UK employer and can lead to permanent settlement.",
        "required_documents": [
            "Valid passport",
            "Job offer from licensed sponsor",
            "Certificate of Sponsorship",
            "Financial evidence (£1,270 for 28 days)",
            "English language certificate",
            "Tuberculosis test (if applicable)",
            "Criminal record certificate"
        ],
        "processing_time": "3 weeks",
        "fee": "£610 - £1,408",
        "eligibility": [
            "Job offer from approved sponsor",
            "Job meets skill level requirement",
            "Salary meets minimum threshold",
            "English language proficiency",
            "Financial requirements met"
        ],
        "application_process": [
            "Receive job offer and Certificate of Sponsorship",
            "Check eligibility requirements",
            "Complete online application",
            "Pay application fee and healthcare surcharge",
            "Book biometric appointment",
            "Submit documents and attend appointment",
            "Wait for decision"
        ]
    },
    {
        "visa_type": "Family Visa",
        "title": "For Partners and Spouses",
        "description": "If you're married to or in a civil partnership with a British citizen or settled person, or have other qualifying family relationships.",
        "required_documents": [
            "Valid passport",
            "Relationship evidence",
            "Financial evidence (£18,600+ annual income)",
            "Accommodation evidence",
            "English language certificate",
            "Tuberculosis test (if applicable)",
            "Marriage/civil partnership certificate"
        ],
        "processing_time": "12 weeks",
        "fee": "£1,538",
        "eligibility": [
            "Genuine relationship with UK partner",
            "Meet financial requirement",
            "Adequate accommodation",
            "English language proficiency",
            "No criminal record issues"
        ],
        "application_process": [
            "Check eligibility requirements",
            "Gather relationship and financial evidence",
            "Take English language test",
            "Complete online application",
            "Book biometric appointment",
            "Submit documents and attend interview if required",
            "Wait for decision"
        ]
    },
    {
        "visa_type": "Visitor Visa",
        "title": "For Short-term Visits and House Hunting",
        "description": "For tourism, visiting family/friends, or business visits up to 6 months. Good for initial house hunting trips.",
        "required_documents": [
            "Valid passport",
            "Bank statements (3-6 months)",
            "Employment letter",
            "Travel itinerary",
            "Accommodation bookings",
            "Return flight tickets",
            "Travel insurance",
            "Invitation letter (if visiting family/friends)"
        ],
        "processing_time": "3 weeks",
        "fee": "£100 for 6 months",
        "eligibility": [
            "Genuine intention to visit temporarily",
            "Sufficient funds for trip",
            "Intention to leave at end of visit",
            "No intention to work (except business activities)",
            "Good immigration history"
        ],
        "application_process": [
            "Complete online application",
            "Pay application fee",
            "Book biometric appointment",
            "Attend appointment with documents",
            "Wait for decision",
            "Collect passport with visa"
        ]
    },
    {
        "visa_type": "Student Visa",
        "title": "For Educational Purposes",
        "description": "If you want to study at a UK university or college, this could also be a pathway to eventual settlement.",
        "required_documents": [
            "Valid passport",
            "Confirmation of Acceptance for Studies (CAS)",
            "Financial evidence",
            "English language certificate",
            "Academic qualifications",
            "Tuberculosis test (if applicable)",
            "Parental consent (if under 18)"
        ],
        "processing_time": "3 weeks",
        "fee": "£348 - £490",
        "eligibility": [
            "Offer from licensed student sponsor",
            "Financial requirements met",
            "English language proficiency",
            "Genuine student intention",
            "Academic progression requirement"
        ],
        "application_process": [
            "Receive offer from UK institution",
            "Get CAS number",
            "Prove financial requirements",
            "Take English test if required",
            "Apply online",
            "Attend biometric appointment",
            "Wait for decision"
        ]
    }
]

# Enhanced Complete 39-Step Relocation Timeline - Updated User Provided List
RELOCATION_TIMELINE = [
    {"id": 1, "title": "Decide on motivation and timeline", "description": "Determine your reasons for moving and establish a realistic timeline for relocation", "category": "Planning", "estimated_days": 7, "dependencies": [], "resources": ["Peak District National Park Authority", "UK Government Moving Guide"], "is_completed": False},
    {"id": 2, "title": "Research UK visa options", "description": "Investigate different visa types available for US citizens moving to UK", "category": "Visa & Legal", "estimated_days": 5, "dependencies": [1], "resources": ["UK Government Visa Guide", "Immigration Lawyer Directory"], "is_completed": False},
    {"id": 3, "title": "Check UK visa eligibility and requirements", "description": "Verify your eligibility for chosen visa type and understand all requirements", "category": "Visa & Legal", "estimated_days": 3, "dependencies": [2], "resources": ["UK Government Portal", "Legal Counsel"], "is_completed": False},
    {"id": 4, "title": "Apply for the most suitable visa", "description": "Submit your visa application with all required documentation", "category": "Visa & Legal", "estimated_days": 7, "dependencies": [3], "resources": ["Application Center", "Document Services"], "is_completed": False},
    {"id": 5, "title": "Gather necessary documents", "description": "Collect passport, proof of funds, certificates, and other required documents", "category": "Documentation", "estimated_days": 14, "dependencies": [4], "resources": ["Document Checklist", "Apostille Services"], "is_completed": False},
    {"id": 6, "title": "Schedule medical exams if required", "description": "Book TB test and other medical examinations as required for visa", "category": "Visa & Legal", "estimated_days": 10, "dependencies": [5], "resources": ["Medical Exam Centers", "TB Testing Centers"], "is_completed": False},
    {"id": 7, "title": "Book biometrics appointment", "description": "Schedule appointment for fingerprints and photograph collection", "category": "Visa & Legal", "estimated_days": 7, "dependencies": [6], "resources": ["VFS Global Centers", "Biometric Services"], "is_completed": False},
    {"id": 8, "title": "Submit visa application", "description": "Complete online application and submit all documentation", "category": "Visa & Legal", "estimated_days": 1, "dependencies": [7], "resources": ["UK Visa Application Centre"], "is_completed": False},
    {"id": 9, "title": "Wait for visa approval", "description": "Processing time varies by visa type - track application status", "category": "Visa & Legal", "estimated_days": 21, "dependencies": [8], "resources": ["Application Tracking Portal"], "is_completed": False},
    {"id": 10, "title": "Receive visa vignette or BRP collection details", "description": "Obtain visa approval and collection instructions", "category": "Visa & Legal", "estimated_days": 3, "dependencies": [9], "resources": ["BRP Collection Centers"], "is_completed": False},
    {"id": 11, "title": "Notify Arizona landlord or list property for sale", "description": "Handle Arizona property arrangements - notice or sale preparation", "category": "US Exit", "estimated_days": 30, "dependencies": [10], "resources": ["Real Estate Agents", "Property Management"], "is_completed": False},
    {"id": 12, "title": "Start decluttering and selling/donating items", "description": "Reduce belongings to essential items for international move", "category": "Logistics", "estimated_days": 21, "dependencies": [11], "resources": ["Donation Centers", "Online Marketplaces"], "is_completed": False},
    {"id": 13, "title": "Get quotes from international movers", "description": "Research and compare international moving company services and costs", "category": "Logistics", "estimated_days": 10, "dependencies": [12], "resources": ["International Moving Companies", "Moving Quotes"], "is_completed": False},
    {"id": 14, "title": "Arrange sea/air shipment of belongings", "description": "Book shipping service for household goods and personal items", "category": "Logistics", "estimated_days": 7, "dependencies": [13], "resources": ["Shipping Companies", "Container Services"], "is_completed": False},
    {"id": 15, "title": "Research currency exchange and transfer methods", "description": "Find best rates for transferring funds from USD to GBP", "category": "Financial", "estimated_days": 5, "dependencies": [10], "resources": ["Currency Exchange Services", "Money Transfer Apps"], "is_completed": False},
    {"id": 16, "title": "Open UK bank account", "description": "Set up UK banking before arrival or arrange digital account", "category": "Financial", "estimated_days": 14, "dependencies": [15], "resources": ["UK Banks", "Online Banking Services"], "is_completed": False},
    {"id": 17, "title": "Sell Arizona car or arrange export", "description": "Dispose of Arizona vehicle or arrange international shipping", "category": "US Exit", "estimated_days": 14, "dependencies": [11], "resources": ["Car Export Services", "Vehicle Sales Platforms"], "is_completed": False},
    {"id": 18, "title": "Cancel Arizona utilities and services", "description": "Terminate utilities, memberships, insurance, and local services", "category": "US Exit", "estimated_days": 7, "dependencies": [17], "resources": ["Utility Companies", "Service Providers"], "is_completed": False},
    {"id": 19, "title": "Book one-way flight to UK", "description": "Purchase flight to Manchester or East Midlands Airport", "category": "Travel", "estimated_days": 3, "dependencies": [10], "resources": ["Flight Booking Sites", "Travel Agents"], "is_completed": False},
    {"id": 20, "title": "Shortlist housing options in Peak District", "description": "Research and identify potential rental or purchase properties", "category": "Housing", "estimated_days": 14, "dependencies": [16], "resources": ["Property Portals", "Estate Agents"], "is_completed": False},
    {"id": 21, "title": "Arrange short-term accommodation", "description": "Book temporary housing for initial weeks in UK", "category": "Housing", "estimated_days": 3, "dependencies": [20], "resources": ["Short-term Rentals", "Hotels"], "is_completed": False},
    {"id": 22, "title": "Arrange airport transport on arrival", "description": "Plan transportation from airport to temporary accommodation", "category": "Travel", "estimated_days": 1, "dependencies": [21], "resources": ["Airport Transport", "Car Rental"], "is_completed": False},
    {"id": 23, "title": "Register with local GP", "description": "Sign up with General Practitioner for NHS healthcare access", "category": "UK Registration", "estimated_days": 7, "dependencies": [22], "resources": ["NHS Registration", "Local Medical Practices"], "is_completed": False},
    {"id": 24, "title": "Finalize UK bank account setup", "description": "Complete in-person bank account verification and setup", "category": "UK Settlement", "estimated_days": 5, "dependencies": [23], "resources": ["Bank Branches", "Account Services"], "is_completed": False},
    {"id": 25, "title": "View and secure long-term housing", "description": "Visit properties and sign lease or purchase agreement", "category": "UK Settlement", "estimated_days": 14, "dependencies": [24], "resources": ["Property Viewings", "Legal Services"], "is_completed": False},
    {"id": 26, "title": "Arrange broadband and utilities", "description": "Set up internet, electricity, gas, and water services", "category": "UK Settlement", "estimated_days": 7, "dependencies": [25], "resources": ["Utility Providers", "Broadband Companies"], "is_completed": False},
    {"id": 27, "title": "Familiarize with transport and driving rules", "description": "Learn UK driving laws and public transport systems", "category": "UK Settlement", "estimated_days": 5, "dependencies": [26], "resources": ["DVLA Information", "Transport Networks"], "is_completed": False},
    {"id": 28, "title": "Exchange driving license or obtain UK license", "description": "Convert US license or apply for new UK driving license", "category": "UK Settlement", "estimated_days": 21, "dependencies": [27], "resources": ["DVLA Services", "Driving Test Centers"], "is_completed": False},
    {"id": 29, "title": "Purchase car or arrange UK car rental", "description": "Buy vehicle or set up long-term car rental arrangement", "category": "UK Settlement", "estimated_days": 7, "dependencies": [28], "resources": ["Car Dealers", "Car Rental Services"], "is_completed": False},
    {"id": 30, "title": "Register for NHS and council tax", "description": "Complete NHS number application and local council registration", "category": "UK Registration", "estimated_days": 14, "dependencies": [29], "resources": ["NHS Services", "Local Council"], "is_completed": False},
    {"id": 31, "title": "Transfer personal documents", "description": "Move medical, education, and legal documents to UK systems", "category": "Documentation", "estimated_days": 21, "dependencies": [30], "resources": ["Document Transfer Services", "Professional Bodies"], "is_completed": False},
    {"id": 32, "title": "Register children in local school", "description": "Enroll children in Peak District area schools if applicable", "category": "UK Settlement", "estimated_days": 14, "dependencies": [31], "resources": ["Local Schools", "Education Authority"], "is_completed": False},
    {"id": 33, "title": "Update address with institutions", "description": "Notify US and UK institutions of address change", "category": "UK Settlement", "estimated_days": 7, "dependencies": [32], "resources": ["Address Change Services", "Government Portals"], "is_completed": False},
    {"id": 34, "title": "File US and UK tax paperwork", "description": "Complete tax obligations in both countries correctly", "category": "Financial", "estimated_days": 14, "dependencies": [33], "resources": ["Tax Advisors", "HMRC Services"], "is_completed": False},
    {"id": 35, "title": "Join local community groups", "description": "Connect with Peak District communities and expat networks", "category": "UK Integration", "estimated_days": 30, "dependencies": [34], "resources": ["Community Groups", "Social Networks"], "is_completed": False},
    {"id": 36, "title": "Explore Peak District area", "description": "Discover local attractions, services, and amenities", "category": "UK Integration", "estimated_days": 60, "dependencies": [35], "resources": ["Local Tourism", "Area Guides"], "is_completed": False},
    {"id": 37, "title": "Meet neighbors and attend local events", "description": "Build social connections in your new community", "category": "UK Integration", "estimated_days": 90, "dependencies": [36], "resources": ["Local Events", "Neighborhood Groups"], "is_completed": False},
    {"id": 38, "title": "Continue learning about UK systems", "description": "Develop understanding of UK culture, laws, and systems", "category": "UK Integration", "estimated_days": 180, "dependencies": [37], "resources": ["Cultural Resources", "Government Information"], "is_completed": False},
    {"id": 39, "title": "Enjoy your new life in Peak District", "description": "Celebrate successful relocation and embrace your new lifestyle", "category": "UK Integration", "estimated_days": 365, "dependencies": [38], "resources": ["Lifestyle Guides", "Local Recommendations"], "is_completed": False}
]

# Enhanced Budget Calculator for $400k
def calculate_relocation_budget(total_budget: float = 400000.0) -> BudgetAnalysis:
    """Calculate comprehensive budget breakdown for $400k relocation"""
    moving_costs = total_budget * 0.0625  # 6.25% = $25k
    visa_fees = total_budget * 0.0125     # 1.25% = $5k  
    initial_housing = total_budget * 0.125 # 12.5% = $50k
    living_expenses = total_budget * 0.1875 # 18.75% = $75k
    emergency_fund = total_budget * 0.125   # 12.5% = $50k
    
    remaining_budget = total_budget - (moving_costs + visa_fees + initial_housing + living_expenses + emergency_fund)
    
    return BudgetAnalysis(
        total_budget=total_budget,
        moving_costs=moving_costs,
        visa_fees=visa_fees, 
        initial_housing=initial_housing,
        living_expenses=living_expenses,
        emergency_fund=emergency_fund,
        remaining_budget=remaining_budget
    )

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return User(**user)

# Initialize default user on startup
async def create_default_user():
    existing_user = await db.users.find_one({"username": "relocate_user"})
    if not existing_user:
        hashed_password = get_password_hash("SecurePass2025!")
        default_user = User(
            username="relocate_user",
            email="relocate@example.com",
            hashed_password=hashed_password,
            current_step=1,
            completed_steps=[]  # Start with no completed steps
        )
        await db.users.insert_one(default_user.dict())
        print("Default user created successfully")

@api_router.post("/analytics/reset")
async def reset_analytics(current_user: User = Depends(get_current_user)):
    """Reset all user progress and analytics to clean state"""
    # Reset user progress
    await db.users.update_one(
        {"username": current_user.username},
        {"$set": {
            "completed_steps": [],
            "current_step": 1
        }}
    )
    
    # Clear progress logs
    await db.progress_logs.delete_many({"user_id": current_user.id})
    
    return {
        "message": "Analytics and progress reset successfully",
        "completed_steps": 0,
        "total_steps": len(RELOCATION_TIMELINE),
        "current_phase": "Planning"
    }

# Password reset endpoints
@api_router.post("/auth/reset-password")
async def request_password_reset(reset_request: PasswordReset):
    user = await db.users.find_one({"username": reset_request.username})
    if not user:
        return {"message": "If the username exists, a reset code will be provided."}
    
    reset_code = "RESET2025"
    await db.password_resets.insert_one({
        "username": reset_request.username,
        "reset_code": reset_code,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    })
    
    return {
        "message": "Reset code generated successfully.",
        "reset_code": reset_code,
        "note": "In production, this code would be sent to your email address."
    }

@api_router.post("/auth/complete-password-reset")
async def complete_password_reset(reset_data: PasswordResetComplete):
    reset_record = await db.password_resets.find_one({
        "username": reset_data.username,
        "reset_code": reset_data.reset_code
    })
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code"
        )
    
    if datetime.utcnow() > reset_record["expires_at"]:
        await db.password_resets.delete_one({"_id": reset_record["_id"]})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset code has expired"
        )
    
    hashed_password = get_password_hash(reset_data.new_password)
    await db.users.update_one(
        {"username": reset_data.username},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    await db.password_resets.delete_one({"_id": reset_record["_id"]})
    return {"message": "Password reset successfully"}

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"username": user_credentials.username})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Enhanced Analytics endpoint with $400k budget analysis
@api_router.get("/analytics/budget")
async def get_budget_analysis(current_user: User = Depends(get_current_user)):
    budget_breakdown = calculate_relocation_budget()
    
    # Calculate progress-based spending
    completed_steps = len(current_user.completed_steps)
    total_steps = len(RELOCATION_TIMELINE)
    progress_percentage = (completed_steps / total_steps) * 100
    
    estimated_spent = budget_breakdown.total_budget * (completed_steps / total_steps) * 0.6  # 60% of progress spent
    
    return {
        "budget_analysis": budget_breakdown.dict(),
        "progress_spending": {
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "progress_percentage": progress_percentage,
            "estimated_spent": estimated_spent,
            "remaining_budget": budget_breakdown.total_budget - estimated_spent
        },
        "spending_recommendations": {
            "next_phase_budget": budget_breakdown.total_budget * 0.15,  # 15% for next phase
            "emergency_reserve": budget_breakdown.emergency_fund,
            "investment_suggestions": [
                "Keep £20k in UK high-yield savings",
                "Consider UK property investment with £100k+",
                "Maintain US investments for currency diversification"
            ]
        }
    }

@api_router.get("/analytics/overview")  
async def get_analytics_overview(current_user: User = Depends(get_current_user)):
    completed_steps = len(current_user.completed_steps)
    total_steps = len(RELOCATION_TIMELINE)
    
    # Calculate category progress
    category_progress = {}
    for step in RELOCATION_TIMELINE:
        category = step["category"]
        if category not in category_progress:
            category_progress[category] = {"total": 0, "completed": 0}
        category_progress[category]["total"] += 1
        if step["id"] in current_user.completed_steps:
            category_progress[category]["completed"] += 1
    
    # Add completion percentages
    for category in category_progress:
        if category_progress[category]["total"] > 0:
            category_progress[category]["percentage"] = (
                category_progress[category]["completed"] / category_progress[category]["total"] * 100
            )
        else:
            category_progress[category]["percentage"] = 0
    
    budget_analysis = calculate_relocation_budget()
    
    return {
        "user_progress": {
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "completion_percentage": (completed_steps / total_steps) * 100,
            "current_phase": get_current_phase(current_user.completed_steps)
        },
        "category_breakdown": category_progress,
        "budget_overview": {
            "total_budget": budget_analysis.total_budget,
            "allocated_funds": {
                "moving": budget_analysis.moving_costs,
                "visa": budget_analysis.visa_fees,
                "housing": budget_analysis.initial_housing,
                "living": budget_analysis.living_expenses,
                "emergency": budget_analysis.emergency_fund
            },
            "available_for_investment": budget_analysis.remaining_budget
        },
        "hospitality_focus": {
            "jobs_available": len([j for j in SAMPLE_JOBS if "Hospitality" in j["category"]]),
            "salary_range": "£18,000 - £35,000",
            "peak_district_opportunities": 8
        }
    }

# Job listings endpoints - Enhanced for hospitality
@api_router.get("/jobs/listings")
async def get_job_listings(category: Optional[str] = None, job_type: Optional[str] = None):
    jobs = []
    for job_data in SAMPLE_JOBS:
        job = JobListing(**job_data)
        if category and job.category != category:
            continue
        if job_type and job.job_type != job_type:
            continue
        jobs.append(job.dict())
    
    return {
        "jobs": jobs,
        "total": len(jobs),
        "categories": list(set([job["category"] for job in [JobListing(**j).dict() for j in SAMPLE_JOBS]])),
        "job_types": list(set([job["job_type"] for job in [JobListing(**j).dict() for j in SAMPLE_JOBS]])),
        "hospitality_focus": {
            "total_hospitality_jobs": len([j for j in jobs if "Hospitality" in j.get("category", "")]),
            "average_salary": "£23,500",
            "peak_district_locations": ["Rowsley", "Chatsworth", "Edale", "Baslow", "Bakewell", "Beeley", "Castleton"]
        }
    }

@api_router.get("/jobs/featured")
async def get_featured_jobs():
    # Return top hospitality jobs first
    featured = sorted(SAMPLE_JOBS, key=lambda x: ("Hospitality" in x["category"], x["posted_date"]), reverse=True)[:6]
    return {"featured_jobs": [JobListing(**job).dict() for job in featured]}

@api_router.get("/jobs/categories")
async def get_job_categories():
    categories = {}
    for job_data in SAMPLE_JOBS:
        job = JobListing(**job_data)
        if job.category not in categories:
            categories[job.category] = []
        categories[job.category].append(job.dict())
    
    return categories

# Visa requirements endpoints
@api_router.get("/visa/requirements")
async def get_visa_requirements():
    return {"visa_types": [VisaRequirement(**req).dict() for req in VISA_REQUIREMENTS]}

@api_router.get("/visa/requirements/{visa_type}")
async def get_visa_requirement_details(visa_type: str):
    for req in VISA_REQUIREMENTS:
        if req["visa_type"].lower().replace(" ", "-") == visa_type.lower():
            return VisaRequirement(**req).dict()
    raise HTTPException(status_code=404, detail="Visa type not found")

@api_router.get("/visa/checklist")
async def get_visa_checklist():
    return {
        "general_documents": [
            "Valid passport (6+ months remaining)",
            "Passport-style photographs",
            "Completed visa application form",
            "Visa application fee payment",
            "Biometric information"
        ],
        "financial_documents": [
            "Bank statements (6 months)",
            "Salary slips or employment letter",
            "Tax returns",
            "Sponsor financial documents (if applicable)"
        ],
        "identity_documents": [
            "Birth certificate",
            "Marriage certificate (if applicable)",
            "Previous passports",
            "Police clearance certificate"
        ],
        "supporting_documents": [
            "TB test results (if required)",
            "English language test certificate",
            "Academic qualifications",
            "Employment contracts or job offers"
        ]
    }

# Timeline and Progress endpoints - Updated for 39 steps
@api_router.get("/timeline/full")
async def get_full_timeline(current_user: User = Depends(get_current_user)):
    user_completed_steps = current_user.completed_steps
    timeline_with_status = []
    
    for step in RELOCATION_TIMELINE:
        step_copy = step.copy()
        step_copy["is_completed"] = step["id"] in user_completed_steps
        timeline_with_status.append(step_copy)
    
    return {
        "timeline": timeline_with_status,
        "total_steps": len(RELOCATION_TIMELINE),
        "completed_steps": len(user_completed_steps),
        "completion_percentage": (len(user_completed_steps) / len(RELOCATION_TIMELINE)) * 100,
        "current_phase": get_current_phase(user_completed_steps),
        "budget_for_phase": calculate_relocation_budget().total_budget / 8  # Budget per phase
    }

@api_router.get("/timeline/public")
async def get_public_timeline():
    """Get timeline without authentication for display purposes"""
    timeline_public = []
    
    for step in RELOCATION_TIMELINE:
        step_copy = step.copy()
        step_copy["is_completed"] = False  # Default to not completed
        timeline_public.append(step_copy)
    
    return {
        "timeline": timeline_public,
        "total_steps": len(RELOCATION_TIMELINE),
        "completed_steps": 0,
        "completion_percentage": 0,
        "current_phase": "Planning"
    }

@api_router.get("/timeline/by-category")
async def get_timeline_by_category(current_user: User = Depends(get_current_user)):
    user_completed_steps = current_user.completed_steps
    categories = {}
    
    for step in RELOCATION_TIMELINE:
        category = step["category"]
        if category not in categories:
            categories[category] = {
                "name": category,
                "steps": [],
                "total_steps": 0,
                "completed_steps": 0
            }
        
        step_copy = step.copy()
        step_copy["is_completed"] = step["id"] in user_completed_steps
        categories[category]["steps"].append(step_copy)
        categories[category]["total_steps"] += 1
        
        if step["id"] in user_completed_steps:
            categories[category]["completed_steps"] += 1
    
    # Calculate completion percentage for each category
    for category in categories.values():
        if category["total_steps"] > 0:
            category["completion_percentage"] = (category["completed_steps"] / category["total_steps"]) * 100
        else:
            category["completion_percentage"] = 0
    
    return categories

@api_router.post("/timeline/update-progress")
async def update_step_progress(progress: TimelineProgressUpdate, current_user: User = Depends(get_current_user)):
    user_completed_steps = current_user.completed_steps.copy()
    
    if progress.completed and progress.step_id not in user_completed_steps:
        user_completed_steps.append(progress.step_id)
    elif not progress.completed and progress.step_id in user_completed_steps:
        user_completed_steps.remove(progress.step_id)
    
    # Update user in database
    await db.users.update_one(
        {"username": current_user.username},
        {"$set": {"completed_steps": user_completed_steps}}
    )
    
    # Log progress update
    await db.progress_logs.insert_one({
        "user_id": current_user.id,
        "step_id": progress.step_id,
        "completed": progress.completed,
        "notes": progress.notes,
        "timestamp": datetime.utcnow()
    })
    
    return {
        "message": "Progress updated successfully",
        "total_completed": len(user_completed_steps),
        "completion_percentage": (len(user_completed_steps) / len(RELOCATION_TIMELINE)) * 100
    }

def get_current_phase(completed_steps):
    """Determine current phase based on completed steps"""
    if not completed_steps:
        return "Planning"
    
    max_completed = max(completed_steps)
    
    if max_completed <= 5:
        return "Planning"
    elif max_completed <= 11:
        return "Visa & Legal"
    elif max_completed <= 18:
        return "Employment"
    elif max_completed <= 23:
        return "Housing"
    elif max_completed <= 28:
        return "Financial"
    elif max_completed <= 33:
        return "Logistics"
    elif max_completed <= 36:
        return "US Exit"
    elif max_completed <= 39:
        return "UK Arrival"
    else:
        return "Settlement"

# Enhanced Resources endpoints - All links for 39 steps with user provided comprehensive list
@api_router.get("/resources/all")
async def get_all_resources():
    return {
        "visa_legal": [
            {"name": "UK Gov Visa & Immigration", "url": "https://www.gov.uk/browse/visas-immigration", "description": "Official UK visa information portal"},
            {"name": "UK Tourist Visa", "url": "https://www.gov.uk/visa-to-visit-uk", "description": "Tourist and visitor visa information"},
            {"name": "UK Skilled Worker Visa", "url": "https://www.gov.uk/skilled-worker-visa", "description": "Employment-based skilled worker visa"},
            {"name": "UK Family Visa", "url": "https://www.gov.uk/uk-family-visa", "description": "Family reunion and spouse visas"},
            {"name": "UK Global Talent Visa", "url": "https://www.gov.uk/global-talent-visa", "description": "For exceptional talent and promise"},
            {"name": "UK Start-up Visa", "url": "https://www.gov.uk/start-up-visa", "description": "For innovative business founders"},
            {"name": "UK Innovator Visa", "url": "https://www.gov.uk/innovator-visa", "description": "For experienced business people"},
            {"name": "UK Ancestry Visa", "url": "https://www.gov.uk/ancestry-visa", "description": "For Commonwealth citizens with UK ancestry"},
            {"name": "UK Divorce/Separation Visa", "url": "https://www.gov.uk/visas-when-you-separate-or-divorce", "description": "Visa options during relationship breakdown"},
            {"name": "UK Settlement", "url": "https://www.gov.uk/settle-in-the-uk", "description": "Permanent residence applications"},
            {"name": "Indefinite Leave to Remain", "url": "https://www.gov.uk/indefinite-leave-to-remain", "description": "Permanent settlement status"},
            {"name": "Migration Expert", "url": "https://www.migrationexpert.co.uk/", "description": "Professional immigration consultation"},
            {"name": "Immigration Lawyers UK", "url": "https://www.immigrationlawyers.co.uk/", "description": "Specialist immigration legal services"},
            {"name": "Davidson Morris", "url": "https://www.davidsonmorris.com/", "description": "Immigration and employment law firm"},
            {"name": "Visa Place", "url": "https://www.visaplace.com/uk-immigration/", "description": "Immigration assistance services"},
            {"name": "Visa First", "url": "https://www.visafirst.com/", "description": "Visa application support service"},
            {"name": "Law Society UK", "url": "https://www.lawsociety.org.uk/", "description": "Find qualified legal professionals"},
            {"name": "Citizens Advice", "url": "https://www.citizensadvice.org.uk/", "description": "Free legal advice and support"}
        ],
        "flights_moving": [
            {"name": "Google Flights", "url": "https://www.google.com/flights", "description": "Flight search and booking platform"},
            {"name": "Skyscanner", "url": "https://www.skyscanner.net/", "description": "Flight comparison and booking"},
            {"name": "Kayak", "url": "https://www.kayak.com/", "description": "Travel search engine"},
            {"name": "Expedia", "url": "https://www.expedia.com/", "description": "Travel booking platform"},
            {"name": "Opodo UK", "url": "https://www.opodo.co.uk/", "description": "Online travel agency"},
            {"name": "International Movers", "url": "https://www.internationalmovers.com/", "description": "Moving company directory"},
            {"name": "Schumacher Cargo", "url": "https://www.schumachercargo.com/", "description": "International shipping services"},
            {"name": "1 Stop Pack N Ship", "url": "https://www.1stoppacknship.com/", "description": "Packing and shipping solutions"},
            {"name": "Matthew James Removals", "url": "https://www.matthewjamesremovals.com/usa-to-uk/", "description": "USA to UK moving specialists"},
            {"name": "Agility Logistics", "url": "https://www.agility.com/en/logistics-services/household-goods-relocation/", "description": "Household goods relocation"},
            {"name": "Ship Overseas", "url": "https://www.shipoverseas.com/", "description": "International shipping platform"},
            {"name": "International Van Lines", "url": "https://www.internationalvanlines.com/", "description": "International moving services"},
            {"name": "uShip", "url": "https://www.uship.com/", "description": "Shipping marketplace platform"}
        ],
        "housing": [
            {"name": "Rightmove", "url": "https://www.rightmove.co.uk/", "description": "UK's largest property portal"},
            {"name": "Zoopla", "url": "https://www.zoopla.co.uk/", "description": "Property search and valuation"},
            {"name": "SpareRoom", "url": "https://www.spareroom.co.uk/", "description": "Room rental and flatshare platform"},
            {"name": "OpenRent", "url": "https://www.openrent.co.uk/", "description": "Direct rental platform"},
            {"name": "Peak District National Park", "url": "https://www.peakdistrict.gov.uk/", "description": "Official Peak District information"},
            {"name": "Peak Cottages", "url": "https://www.peakcottages.com/", "description": "Peak District holiday and rental properties"},
            {"name": "Prime Location Peak District", "url": "https://www.primelocation.com/to-rent/property/peak-district-national-park/", "description": "Premium Peak District properties"},
            {"name": "Rightmove Peak District", "url": "https://www.rightmove.co.uk/property-to-rent/find/Peak-District.html", "description": "Peak District property rentals"},
            {"name": "OnTheMarket Peak District", "url": "https://www.onthemarket.com/to-rent/property/peak-district-national-park/", "description": "Peak District property listings"},
            {"name": "Bagshaws Residential", "url": "https://www.bagshawsresidential.co.uk/", "description": "Local Peak District estate agents"},
            {"name": "Sally Botham Estate Agents", "url": "https://www.sallybotham.co.uk/", "description": "Peak District property specialists"},
            {"name": "Fidler Taylor Estate Agents", "url": "https://www.fidler-taylor.co.uk/", "description": "Local property agents"}
        ],
        "expat_communities": [
            {"name": "British Expats Forum", "url": "https://britishexpats.com/forum/", "description": "UK expat community forum"},
            {"name": "Expat.com UK", "url": "https://www.expat.com/en/destination/europe/england/", "description": "UK expat information and community"},
            {"name": "InterNations UK", "url": "https://internations.org/united-kingdom-expats", "description": "Global expat community in UK"},
            {"name": "Expat Focus UK", "url": "https://www.expatfocus.com/united-kingdom", "description": "UK expat advice and community"},
            {"name": "Just Landed UK", "url": "https://www.justlanded.com/english/United-Kingdom", "description": "UK expat guide and resources"},
            {"name": "Meetup Expat UK", "url": "https://www.meetup.com/topics/expat/gb/", "description": "Expat meetups across UK"},
            {"name": "InterNations Manchester", "url": "https://internations.org/manchester-expats", "description": "Manchester expat community"},
            {"name": "Expatica UK", "url": "https://www.expatica.com/uk/", "description": "Expat news and information hub"},
            {"name": "Manchester International Friends", "url": "https://www.meetup.com/manchester-international-friends/", "description": "Find expat meetups and social events"},
            {"name": "British Expats UK Forum", "url": "https://britishexpats.com/forum/united-kingdom-76/", "description": "Forum and community for expats in the UK"},
            {"name": "Manchester Expats Facebook", "url": "https://www.facebook.com/groups/manchesterexpats/", "description": "Community-driven groups for connecting with locals and expats"}
        ],
        "healthcare": [
            {"name": "NHS Moving to England", "url": "https://www.nhs.uk/using-the-nhs/moving-to-england-from-abroad/", "description": "NHS services for newcomers"},
            {"name": "NHS Official Website", "url": "https://www.nhs.uk/", "description": "National Health Service portal"},
            {"name": "NHS Migrant Health Guide", "url": "https://www.gov.uk/guidance/nhs-entitlements-migrant-health-guide", "description": "Healthcare entitlements for migrants"},
            {"name": "Bupa Health Insurance", "url": "https://www.bupa.co.uk/health/health-insurance", "description": "Private health insurance options"},
            {"name": "Aviva Health Insurance", "url": "https://www.aviva.co.uk/health/health-insurance/", "description": "Private healthcare cover"},
            {"name": "AXA Global Healthcare", "url": "https://www.axaglobalhealthcare.com/", "description": "International health insurance"},
            {"name": "NHS GP Registration", "url": "https://www.nhs.uk/nhs-services/gps/how-to-register-with-a-gp-surgery/", "description": "How to register with a local GP in the UK"},
            {"name": "Bupa UK", "url": "https://www.bupa.co.uk/", "description": "Private health insurance and services"},
            {"name": "AXA Health", "url": "https://www.axahealth.co.uk/", "description": "Private healthcare provider"},
            {"name": "General Medical Council", "url": "https://www.gmc-uk.org/", "description": "Regulator of UK doctors — find a doctor"}
        ],
        "financial": [
            {"name": "HSBC UK", "url": "https://www.hsbc.co.uk/", "description": "Major UK banking services"},
            {"name": "Lloyds Bank", "url": "https://www.lloydsbank.com/", "description": "Established UK bank"},
            {"name": "Barclays", "url": "https://www.barclays.co.uk/", "description": "Global banking services"},
            {"name": "Nationwide", "url": "https://www.nationwide.co.uk/", "description": "UK building society"},
            {"name": "Santander UK", "url": "https://www.santander.co.uk/", "description": "International banking in UK"},
            {"name": "Revolut", "url": "https://www.revolut.com/", "description": "Digital banking platform"},
            {"name": "Wise UK", "url": "https://wise.com/gb/", "description": "International money transfers"},
            {"name": "Monzo", "url": "https://www.monzo.com/", "description": "Mobile-first banking"},
            {"name": "Starling Bank", "url": "https://www.starlingbank.com/", "description": "Digital banking services"},
            {"name": "Wise Money Transfer", "url": "https://wise.com/", "description": "Currency exchange and transfers"},
            {"name": "CurrencyFair", "url": "https://www.currencyfair.com/", "description": "Peer-to-peer currency exchange"},
            {"name": "XE Currency", "url": "https://www.xe.com/", "description": "Currency rates and transfers"},
            {"name": "Remitly UK", "url": "https://www.remitly.com/gb/en", "description": "International money transfers"}
        ],
        "transport_driving": [
            {"name": "UK Non-GB License", "url": "https://www.gov.uk/driving-nongb-licence", "description": "Driving with foreign license in UK"},
            {"name": "Exchange Foreign License", "url": "https://www.gov.uk/exchange-foreign-driving-licence", "description": "Converting foreign driving license"},
            {"name": "National Rail", "url": "https://www.nationalrail.co.uk/", "description": "UK railway network information"},
            {"name": "TfGM Trains", "url": "https://www.tfgm.com/public-transport/train", "description": "Greater Manchester train services"},
            {"name": "Traveline", "url": "https://www.traveline.info/", "description": "UK public transport planner"},
            {"name": "Trainline", "url": "https://www.trainline.com/", "description": "Train ticket booking platform"},
            {"name": "Manchester Public Transport", "url": "https://www.introducingmanchester.com/public-transport", "description": "Manchester area transport guide"},
            {"name": "Transport for Greater Manchester", "url": "https://www.tfgm.com/", "description": "Local public transport authority"},
            {"name": "National Rail Official", "url": "https://www.nationalrail.co.uk/", "description": "Train schedules and tickets"},
            {"name": "Stagecoach Manchester", "url": "https://www.stagecoachbus.com/about/manchester", "description": "Bus services in Greater Manchester"},
            {"name": "DVLA Driving License Services", "url": "https://www.gov.uk/browse/driving/driving-licences", "description": "Apply, renew or exchange your UK driving license"},
            {"name": "Trainline Booking", "url": "https://www.thetrainline.com/", "description": "Rail ticket booking and information"}
        ],
        "education": [
            {"name": "Find School in England", "url": "https://www.gov.uk/find-school-in-england", "description": "Official school finder tool"},
            {"name": "School Performance Data", "url": "https://www.compare-school-performance.service.gov.uk/", "description": "Compare school performance data"},
            {"name": "Independent Schools Council", "url": "https://www.isc.co.uk/", "description": "Private school information"},
            {"name": "Universities UK", "url": "https://www.universitiesuk.ac.uk/", "description": "University sector representation"},
            {"name": "Study UK British Council", "url": "https://www.study-uk.britishcouncil.org/", "description": "Official UK education guide"},
            {"name": "Gov.uk School Performance", "url": "https://www.gov.uk/school-performance-tables", "description": "Official school comparison and search"},
            {"name": "Manchester Education Services", "url": "https://www.manchester.gov.uk/info/200062/education_and_schools", "description": "Local education services and information"},
            {"name": "UCAS University Applications", "url": "https://www.ucas.com/", "description": "University admissions service for UK higher education"},
            {"name": "International Schools Manchester", "url": "https://www.international-schools-database.com/in/manchester", "description": "Directory of international schools in Manchester"},
            {"name": "Ofsted Reports", "url": "https://reports.ofsted.gov.uk/", "description": "School quality inspections and ratings"}
        ],
        "legal_tax": [
            {"name": "UK Tax on Foreign Income", "url": "https://www.gov.uk/tax-foreign-income", "description": "Tax obligations on overseas income"},
            {"name": "UK Retirement Tax", "url": "https://www.gov.uk/tax-right-retire-abroad-return-to-uk", "description": "Tax rules for returning retirees"},
            {"name": "UK Residence Tax", "url": "https://www.gov.uk/uk-residence-tax", "description": "UK tax residence rules"},
            {"name": "Capital Gains Tax", "url": "https://www.gov.uk/capital-gains-tax", "description": "UK capital gains tax guide"},
            {"name": "HMRC", "url": "https://www.hmrc.gov.uk/", "description": "UK tax authority"},
            {"name": "Greenback Tax Services", "url": "https://www.greenbacktaxservices.com/", "description": "US expat tax specialists"},
            {"name": "Bright Tax", "url": "https://brighttax.com/", "description": "Expat tax preparation"},
            {"name": "Expatriate Tax Returns", "url": "https://www.expatriatetaxreturns.com/", "description": "US expat tax services"},
            {"name": "Tax Samaritan", "url": "https://www.taxsamaritan.com/", "description": "US tax services for expats"},
            {"name": "US Tax FS", "url": "https://www.ustaxfs.com/", "description": "US tax filing services"},
            {"name": "HMRC Official", "url": "https://www.gov.uk/government/organisations/hm-revenue-customs", "description": "UK tax authority — Self-assessment, PAYE, etc."},
            {"name": "Citizens Advice", "url": "https://www.citizensadvice.org.uk/", "description": "Free legal and tax advice"},
            {"name": "GOV.UK Tax Guide", "url": "https://www.gov.uk/tax-uk", "description": "UK tax guidance for newcomers"},
            {"name": "Law Society Solicitor Search", "url": "https://solicitors.lawsociety.org.uk/", "description": "Search for qualified solicitors in the UK"},
            {"name": "TaxAid", "url": "https://taxaid.org.uk/", "description": "Help with tax problems for low-income individuals"}
        ],
        "peak_district_lifestyle": [
            {"name": "Visit Peak District", "url": "https://www.visitpeakdistrict.com/", "description": "Official Peak District tourism"},
            {"name": "Peak District Organization", "url": "https://www.peakdistrict.org/", "description": "Peak District information hub"},
            {"name": "Peak District Visiting", "url": "https://www.peakdistrict.gov.uk/visiting", "description": "Visitor information and guides"},
            {"name": "Derbyshire Dales Council", "url": "https://www.derbyshiredales.gov.uk/", "description": "Local council services"},
            {"name": "High Peak Council", "url": "https://www.highpeak.gov.uk/", "description": "High Peak local authority"},
            {"name": "Derbyshire County Council", "url": "https://www.derbyshire.gov.uk/home.aspx", "description": "County-wide services"},
            {"name": "Peak District Learning", "url": "https://www.peakdistrict.gov.uk/learning-about", "description": "Educational resources"},
            {"name": "Peak District Facebook Group", "url": "https://www.facebook.com/groups/peakdistrict/", "description": "Peak District community group"},
            {"name": "Peak District Community", "url": "https://www.facebook.com/groups/1602339603425897/", "description": "Local community discussions"},
            {"name": "Derbyshire Expats", "url": "https://www.facebook.com/groups/derbyshireexpats/", "description": "Derbyshire expat community"},
            {"name": "Derbyshire Events", "url": "https://www.eventbrite.co.uk/d/united-kingdom--derbyshire/events/", "description": "Local events and activities"},
            {"name": "Derbyshire Meetups", "url": "https://www.meetup.com/cities/gb/derbyshire/", "description": "Meetup groups in Derbyshire"},
            {"name": "Visit Peak District & Derbyshire", "url": "https://www.visitpeakdistrict.com/", "description": "Official tourism site"},
            {"name": "Peak District National Park Authority", "url": "https://www.peakdistrict.gov.uk/", "description": "National Park official site — events, conservation, walks"},
            {"name": "Peak District Walks", "url": "https://peakdistrictwalks.net/", "description": "Detailed guides for local walks"},
            {"name": "Peak District Online", "url": "https://www.peakdistrictonline.co.uk/", "description": "Local news, community, and activities"},
            {"name": "Derbyshire Life", "url": "https://www.derbyshirelife.co.uk/", "description": "Lifestyle magazine covering Peak District and Derbyshire"}
        ],
        "miscellaneous": [
            {"name": "Forward2Me", "url": "https://www.forward2me.com/", "description": "UK parcel forwarding service"},
            {"name": "ReShip", "url": "https://www.reship.com/", "description": "International package forwarding"},
            {"name": "My UK Mailbox", "url": "https://www.myukmailbox.com/", "description": "UK postal address service"},
            {"name": "GiffGaff", "url": "https://www.giffgaff.com/", "description": "UK mobile network provider"},
            {"name": "Lebara UK", "url": "https://www.lebara.co.uk/", "description": "International mobile services"},
            {"name": "Lycamobile UK", "url": "https://www.lycamobile.co.uk/", "description": "International calling plans"},
            {"name": "Vodafone UK", "url": "https://www.vodafone.co.uk/", "description": "Major UK mobile network"},
            {"name": "O2 UK", "url": "https://www.o2.co.uk/", "description": "UK mobile and broadband services"}
        ]
    }

@api_router.get("/resources/search")
async def search_resources(q: str = ""):
    """Search across all resources"""
    if not q or len(q.strip()) < 2:
        return {"results": [], "total": 0, "query": q}
    
    query = q.lower().strip()
    all_resources = await get_all_resources()
    results = []
    
    for category, resources in all_resources.items():
        for resource in resources:
            # Search in name, description, and URL
            if (query in resource["name"].lower() or 
                query in resource["description"].lower() or 
                query in resource["url"].lower()):
                results.append({
                    **resource,
                    "category": category.replace("_", " ").title()
                })
    
    return {
        "results": results,
        "total": len(results),
        "query": q
    }
    return {
        "visa_legal": [
            {"name": "UK Government Visa Guide", "url": "https://www.gov.uk/browse/visas-immigration", "description": "Official UK visa information"},
            {"name": "Immigration Lawyer Directory", "url": "https://www.lawsociety.org.uk", "description": "Find qualified immigration lawyers"},
            {"name": "Document Apostille Services", "url": "https://www.gov.uk/get-document-legalised", "description": "Document legalization services"},
            {"name": "Visa Application Centre", "url": "https://www.vfsglobal.co.uk", "description": "UK visa application centres"},
            {"name": "UK.gov Immigration Rules", "url": "https://www.gov.uk/guidance/immigration-rules", "description": "Detailed immigration rules"},
            {"name": "Home Office Contact", "url": "https://www.gov.uk/contact-ukvi-inside-outside-uk", "description": "Home Office immigration contact"},
            {"name": "TB Testing Centers", "url": "https://www.gov.uk/tb-test-visa", "description": "Tuberculosis testing for visas"},
            {"name": "IELTS Registration", "url": "https://www.ielts.org", "description": "English language testing"},
            {"name": "TOEFL Registration", "url": "https://www.ets.org/toefl", "description": "Alternative English testing"},
            {"name": "Police Certificate Guide", "url": "https://www.gov.uk/criminal-record-checks-apply-role", "description": "Criminal record checks"},
            {"name": "Immigration Health Surcharge", "url": "https://www.gov.uk/healthcare-immigration-application", "description": "NHS healthcare payments"},
            {"name": "Biometric Residence Permits", "url": "https://www.gov.uk/biometric-residence-permits", "description": "BRP information"},
            {"name": "Settlement Applications", "url": "https://www.gov.uk/settle-in-the-uk", "description": "Permanent residence guide"},
            {"name": "British Citizenship", "url": "https://www.gov.uk/apply-citizenship-spouse", "description": "Citizenship applications"},
            {"name": "Immigration Appeals", "url": "https://www.gov.uk/immigration-asylum-tribunal", "description": "Appeal process information"},
            {"name": "FBI Background Check", "url": "https://www.fbi.gov/how-we-can-help-you/need-an-fbi-service-or-more-information/identity-history-summary-checks", "description": "US criminal background verification"},
            {"name": "Medical Exam Locations", "url": "https://www.gov.uk/tb-test-visa", "description": "Approved medical examination centers"},
            {"name": "Biometric Services", "url": "https://www.vfsglobal.co.uk", "description": "Biometric appointment booking"}
        ],
        "housing": [
            {"name": "Rightmove", "url": "https://www.rightmove.co.uk", "description": "UK's largest property portal"},
            {"name": "Zoopla", "url": "https://www.zoopla.co.uk", "description": "Property search and valuation"},
            {"name": "SpareRoom", "url": "https://www.spareroom.co.uk", "description": "Room rental and flatshare platform"},
            {"name": "Peak District Property", "url": "https://www.peakdistrictproperty.co.uk", "description": "Local estate agents in Peak District"},
            {"name": "OpenRent", "url": "https://www.openrent.co.uk", "description": "Direct rental platform"},
            {"name": "PropertyFinder", "url": "https://www.propertyfinder.com/uk", "description": "Property search engine"},
            {"name": "Gumtree Rentals", "url": "https://www.gumtree.com/flats-houses", "description": "Classified property ads"},
            {"name": "Facebook Marketplace", "url": "https://www.facebook.com/marketplace/category/propertyrentals", "description": "Social media rentals"},
            {"name": "Council Tax Information", "url": "https://www.gov.uk/council-tax", "description": "Local taxation guide"},
            {"name": "Mortgage Information", "url": "https://www.moneyadviceservice.org.uk/en/categories/mortgages", "description": "Home buying advice"},
            {"name": "Tenant Rights Guide", "url": "https://www.shelter.org.uk", "description": "Housing rights charity"},
            {"name": "Property Investment", "url": "https://www.propertyinvestor.co.uk", "description": "Investment properties"},
            {"name": "HomeViews", "url": "https://www.homeviews.com", "description": "Development reviews"},
            {"name": "PropertyData", "url": "https://propertydata.co.uk", "description": "Market analysis"},
            {"name": "Land Registry", "url": "https://www.gov.uk/government/organisations/land-registry", "description": "Property ownership records"},
            {"name": "Deposit Protection", "url": "https://www.gov.uk/tenancy-deposit-protection", "description": "Tenant deposit schemes"},
            {"name": "Housing Benefit", "url": "https://www.gov.uk/housing-benefit", "description": "Housing assistance programs"},
            {"name": "Local Authority Housing", "url": "https://www.gov.uk/apply-for-council-housing", "description": "Council housing applications"}
        ],
        "employment": [
            {"name": "Indeed UK", "url": "https://uk.indeed.com", "description": "Job search platform"},
            {"name": "Reed", "url": "https://www.reed.co.uk", "description": "UK recruitment website"},
            {"name": "LinkedIn UK", "url": "https://www.linkedin.com/jobs", "description": "Professional networking and jobs"},
            {"name": "Peak District Jobs", "url": "https://www.peakdistrictjobs.co.uk", "description": "Local job opportunities"},
            {"name": "Totaljobs", "url": "https://www.totaljobs.com", "description": "Major job board"},
            {"name": "CV-Library", "url": "https://www.cv-library.co.uk", "description": "CV and job matching"},
            {"name": "Glassdoor UK", "url": "https://www.glassdoor.co.uk", "description": "Company reviews and salaries"},
            {"name": "Guardian Jobs", "url": "https://jobs.theguardian.com", "description": "Professional opportunities"},
            {"name": "Jobsite", "url": "https://www.jobsite.co.uk", "description": "Online job search"},
            {"name": "Monster UK", "url": "https://www.monster.co.uk", "description": "Career development"},
            {"name": "Fish4Jobs", "url": "https://www.fish4.co.uk/jobs", "description": "Regional job search"},
            {"name": "CWJobs", "url": "https://www.cwjobs.co.uk", "description": "IT and tech jobs"},
            {"name": "JobServe", "url": "https://www.jobserve.com", "description": "Technology careers"},
            {"name": "Robert Half", "url": "https://www.roberthalf.co.uk", "description": "Professional recruitment"},
            {"name": "Hays Recruitment", "url": "https://www.hays.co.uk", "description": "Specialist recruitment"},
            {"name": "Michael Page", "url": "https://www.michaelpage.co.uk", "description": "Executive search"},
            {"name": "Adecco", "url": "https://www.adecco.co.uk", "description": "Temporary and permanent roles"},
            {"name": "Randstad", "url": "https://www.randstad.co.uk", "description": "Global recruitment"},
            {"name": "Manpower", "url": "https://www.manpower.co.uk", "description": "Workforce solutions"},
            {"name": "Kelly Services", "url": "https://www.kellyservices.co.uk", "description": "Professional staffing"},
            {"name": "UK Hospitality", "url": "https://www.ukhospitality.org.uk", "description": "Hospitality industry association"},
            {"name": "Caterer.com", "url": "https://www.caterer.com/jobs", "description": "Hospitality job specialists"},
            {"name": "HospoJobs", "url": "https://hospojobs.com", "description": "Hospitality recruitment platform"},
            {"name": "Hotel Jobs UK", "url": "https://www.hoteljobs.co.uk", "description": "Hotel and restaurant positions"},
            {"name": "Hospitality Recruitment", "url": "https://www.hospitalityrecruitment.co.uk", "description": "Specialized hospitality agency"}
        ],
        "financial": [
            {"name": "Monzo", "url": "https://monzo.com", "description": "Digital bank popular with expats"},
            {"name": "Wise", "url": "https://wise.com", "description": "International money transfers"},
            {"name": "HMRC", "url": "https://www.gov.uk/government/organisations/hm-revenue-customs", "description": "UK tax authority"},
            {"name": "NHS Registration", "url": "https://www.nhs.uk/using-the-nhs/nhs-services/gps/how-to-register-with-a-gp-practice/", "description": "Healthcare registration"},
            {"name": "Starling Bank", "url": "https://www.starlingbank.com", "description": "Digital banking"},
            {"name": "HSBC Expat", "url": "https://www.hsbc.co.uk/international/moving-to-uk", "description": "International banking"},
            {"name": "Barclays International", "url": "https://www.barclays.co.uk/international-banking", "description": "Global banking services"},
            {"name": "Lloyds International", "url": "https://www.lloydsbank.com/international", "description": "International accounts"},
            {"name": "Santander UK", "url": "https://www.santander.co.uk", "description": "Spanish bank UK operations"},
            {"name": "Western Union", "url": "https://www.westernunion.com/gb/en/home.html", "description": "Money transfer service"},
            {"name": "Remitly", "url": "https://www.remitly.com/gb/en", "description": "Digital remittance"},
            {"name": "Azimo", "url": "https://azimo.com", "description": "International transfers"},
            {"name": "CurrencyFair", "url": "https://www.currencyfair.com", "description": "Peer-to-peer exchange"},
            {"name": "XE Money", "url": "https://www.xe.com/money-transfer", "description": "Currency exchange"},
            {"name": "Revolut", "url": "https://www.revolut.com", "description": "Digital financial services"},
            {"name": "UK Credit Reference", "url": "https://www.experian.co.uk", "description": "Credit reports and scores"},
            {"name": "Equifax UK", "url": "https://www.equifax.co.uk", "description": "Credit monitoring"},
            {"name": "TransUnion UK", "url": "https://www.transunion.co.uk", "description": "Credit information"},
            {"name": "Money Advice Service", "url": "https://www.moneyadviceservice.org.uk", "description": "Free financial guidance"},
            {"name": "Citizens Advice", "url": "https://www.citizensadvice.org.uk", "description": "Financial advice charity"},
            {"name": "Tax Advisory Partnership", "url": "https://www.taxadviserpartnership.com", "description": "Expat tax specialists"},
            {"name": "International Tax Planning", "url": "https://www.internationaltaxplanning.com", "description": "Cross-border tax advice"}
        ],
        "local_services": [
            {"name": "Peak District National Park", "url": "https://www.peakdistrict.gov.uk", "description": "Official park information"},
            {"name": "Derbyshire County Council", "url": "https://www.derbyshire.gov.uk", "description": "Local government services"},
            {"name": "Peak District Chamber", "url": "https://www.peakdistrictchamber.co.uk", "description": "Business networking"},
            {"name": "Local Community Groups", "url": "https://www.facebook.com/groups/peakdistrictexpats", "description": "Expat community support"},
            {"name": "Sheffield City Council", "url": "https://www.sheffield.gov.uk", "description": "Nearby major city services"},
            {"name": "Manchester City Council", "url": "https://www.manchester.gov.uk", "description": "Regional urban center"},
            {"name": "Nottingham City Council", "url": "https://www.nottinghamcity.gov.uk", "description": "East Midlands services"},
            {"name": "NHS Peak District", "url": "https://www.derbyshirecommunityhealth.nhs.uk", "description": "Local health services"},
            {"name": "Derbyshire Police", "url": "https://www.derbyshire.police.uk", "description": "Local law enforcement"},
            {"name": "Peak District Fire", "url": "https://www.derbys-fire.gov.uk", "description": "Emergency services"},
            {"name": "High Peak Council", "url": "https://www.highpeak.gov.uk", "description": "Local district council"},
            {"name": "Derbyshire Dales Council", "url": "https://www.derbyshiredales.gov.uk", "description": "Southern Peak District"},
            {"name": "Staffordshire Moorlands", "url": "https://www.staffsmoorlands.gov.uk", "description": "Western Peak area"},
            {"name": "Local Library Services", "url": "https://www.derbyshire.gov.uk/leisure/libraries", "description": "Public libraries"},
            {"name": "Adult Education", "url": "https://www.derby.ac.uk", "description": "Further education opportunities"},
            {"name": "GP Registration", "url": "https://www.nhs.uk/using-the-nhs/nhs-services/gps/how-to-register-with-a-gp-practice/", "description": "Medical practice registration"},
            {"name": "Council Services", "url": "https://www.gov.uk/find-local-council", "description": "Local authority services"},
            {"name": "National Insurance", "url": "https://www.gov.uk/apply-national-insurance-number", "description": "NI number application"}
        ],
        "lifestyle": [
            {"name": "Visit Peak District", "url": "https://www.visitpeakdistrict.com", "description": "Tourism and attractions"},
            {"name": "Peak District Weather", "url": "https://www.metoffice.gov.uk", "description": "Weather forecasts"},
            {"name": "Public Transport", "url": "https://www.travelsouthyorkshire.com", "description": "Local transport information"},
            {"name": "Healthcare Finder", "url": "https://www.nhs.uk/service-search", "description": "Find local healthcare services"},
            {"name": "National Trust", "url": "https://www.nationaltrust.org.uk/peak-district", "description": "Heritage sites"},
            {"name": "English Heritage", "url": "https://www.english-heritage.org.uk", "description": "Historic properties"},
            {"name": "Peak Rail", "url": "https://www.peakrail.co.uk", "description": "Heritage railway"},
            {"name": "Chatsworth House", "url": "https://www.chatsworth.org", "description": "Historic estate"},
            {"name": "Blue John Cavern", "url": "https://www.bluejohn-cavern.co.uk", "description": "Underground attractions"},
            {"name": "Buxton Opera House", "url": "https://www.buxtonoperahouse.org.uk", "description": "Cultural venues"},
            {"name": "Peak Shopping", "url": "https://www.mcarthurglen.com/uk/designer-outlet-east-midlands", "description": "Shopping centers"},
            {"name": "Local Farmers Markets", "url": "https://www.peakdistrictfarmersmarkets.co.uk", "description": "Fresh local produce"},
            {"name": "Peak District Pubs", "url": "https://www.peakdistrictpubs.co.uk", "description": "Traditional inns"},
            {"name": "Hiking Clubs", "url": "https://www.ramblers.org.uk", "description": "Walking groups"},
            {"name": "Cycling Routes", "url": "https://www.sustrans.org.uk", "description": "Cycle path network"},
            {"name": "Rock Climbing", "url": "https://www.ukclimbing.com/logbook/areas/peak_district", "description": "Climbing locations"},
            {"name": "Local Golf Courses", "url": "https://www.peakdistrictgolf.co.uk", "description": "Golf facilities"},
            {"name": "Riding Schools", "url": "https://www.peakdistrictridingschools.co.uk", "description": "Equestrian activities"},
            {"name": "Local Events", "url": "https://www.peakdistrictonline.co.uk/events", "description": "Community events"},
            {"name": "Arts & Crafts", "url": "https://www.peakdistrictartsandcrafts.co.uk", "description": "Local artisans"}
        ],
        "moving_logistics": [
            {"name": "Crown Relocations", "url": "https://www.crownrelo.com", "description": "Premium international moving"},
            {"name": "Allied International", "url": "https://www.allied.com", "description": "Comprehensive moving services"},
            {"name": "Ship Smart", "url": "https://www.shipsmart.com", "description": "Container shipping"},
            {"name": "Seven Seas Worldwide", "url": "https://www.sevenseasworldwide.com", "description": "International shipping"},
            {"name": "FedEx International", "url": "https://www.fedex.com", "description": "Express shipping"},
            {"name": "BigSteelBox", "url": "https://www.bigsteelbox.com", "description": "Portable storage"},
            {"name": "UPakWeShip", "url": "https://www.upakweship.com", "description": "Self-pack shipping"},
            {"name": "My Baggage", "url": "https://www.mybaggage.com", "description": "Student shipping"},
            {"name": "Send My Bag", "url": "https://www.sendmybag.com", "description": "Luggage shipping"},
            {"name": "Excess Baggage", "url": "https://www.excess-baggage.com", "description": "Airline excess shipping"},
            {"name": "International Moving Quotes", "url": "https://www.internationalmovers.com", "description": "Moving company comparison"},
            {"name": "Customs Brokers", "url": "https://www.gov.uk/guidance/list-of-customs-agents-and-fast-parcel-operators", "description": "UK customs clearance"},
            {"name": "Pet Relocation", "url": "https://www.gov.uk/bring-pet-to-great-britain", "description": "Pet import procedures"},
            {"name": "Vehicle Import", "url": "https://www.gov.uk/importing-vehicles-into-the-uk", "description": "Car import guidelines"}
        ],
        "education": [
            {"name": "University of Derby", "url": "https://www.derby.ac.uk", "description": "Local university"},
            {"name": "Sheffield Hallam University", "url": "https://www.shu.ac.uk", "description": "Nearby university"},
            {"name": "University of Sheffield", "url": "https://www.sheffield.ac.uk", "description": "Research university"},
            {"name": "Nottingham Trent University", "url": "https://www.ntu.ac.uk", "description": "Regional university"},
            {"name": "UCAS Applications", "url": "https://www.ucas.com", "description": "University applications"},
            {"name": "Adult Learning", "url": "https://www.gov.uk/further-education-courses", "description": "Continuing education"},
            {"name": "Online Learning", "url": "https://www.futurelearn.com", "description": "Digital courses"},
            {"name": "Student Finance", "url": "https://www.gov.uk/student-finance", "description": "Education funding"},
            {"name": "Apprenticeships", "url": "https://www.gov.uk/apply-apprenticeship", "description": "Work-based learning"},
            {"name": "Professional Development", "url": "https://www.cipd.co.uk", "description": "Career advancement courses"}
        ],
        "additional_resources": [
            {"name": "UK Postcode Finder", "url": "https://www.royalmail.com/find-a-postcode", "description": "Find UK postcodes and addresses"},
            {"name": "UK Weather Service", "url": "https://www.metoffice.gov.uk", "description": "Official UK weather forecasts"},
            {"name": "UK Driver's License", "url": "https://www.gov.uk/driving-licence-application", "description": "Apply for UK driving license"},
            {"name": "UK TV License", "url": "https://www.tvlicensing.co.uk", "description": "Required for watching live TV"},
            {"name": "Compare UK Utilities", "url": "https://www.comparethemarket.com", "description": "Compare energy and utility providers"},
            {"name": "UK Broadband Comparison", "url": "https://www.moneysavingexpert.com/broadband", "description": "Find best internet deals"},
            {"name": "UK Mobile Networks", "url": "https://www.ofcom.org.uk/phones-telecoms-and-internet/advice-for-consumers/mobile-coverage-checker", "description": "Check mobile coverage"},
            {"name": "UK Charity Support", "url": "https://www.citizensadvice.org.uk", "description": "Free advice and support"},
            {"name": "UK Emergency Services", "url": "https://www.gov.uk/emergency-services", "description": "Police, fire, ambulance contacts"},
            {"name": "UK Consumer Rights", "url": "https://www.gov.uk/consumer-protection-rights", "description": "Know your consumer rights"},
            {"name": "Peak District Walks", "url": "https://www.peakdistrictwalks.com", "description": "Detailed walking guides"},
            {"name": "Peak District Photography", "url": "https://www.peakdistrictphotography.co.uk", "description": "Photography locations and tips"},
            {"name": "Peak District Wildlife", "url": "https://www.derbyshirewildlifetrust.org.uk", "description": "Local wildlife conservation"},
            {"name": "Peak District History", "url": "https://www.peakdistricthistory.org.uk", "description": "Local history and heritage"},
            {"name": "Peak District Climbing", "url": "https://www.peakdistrictclimbing.co.uk", "description": "Rock climbing information"},
            {"name": "Peak District Cycling", "url": "https://www.peakdistrictcycling.co.uk", "description": "Cycling routes and rentals"}
        ]
    }

# Dashboard overview with enhanced stats
@api_router.get("/dashboard/overview")
async def get_dashboard_overview(current_user: User = Depends(get_current_user)):
    total_steps = len(RELOCATION_TIMELINE)
    completed_steps = len(current_user.completed_steps)
    
    # Calculate in progress tasks (next 3 uncompleted steps)
    in_progress = 0
    urgent_tasks = 0
    
    for step in RELOCATION_TIMELINE:
        if step["id"] not in current_user.completed_steps:
            if in_progress < 3:
                in_progress += 1
            if step["category"] in ["Visa & Legal", "Employment"]:
                urgent_tasks += 1
    
    return {
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "in_progress": in_progress,
        "urgent_tasks": urgent_tasks,
        "current_phase": get_current_phase(current_user.completed_steps),
        "budget_summary": {
            "total_budget": 400000,
            "allocated": 205000,
            "remaining": 195000
        },
        "hospitality_jobs": len([j for j in SAMPLE_JOBS if "Hospitality" in j["category"]])
    }

# Progress tracking endpoints
@api_router.get("/progress/items")
async def get_progress_items(current_user: User = Depends(get_current_user), category: Optional[str] = None, status: Optional[str] = None):
    # Generate progress items based on timeline and completion status
    items = []
    
    for step in RELOCATION_TIMELINE:
        if category and step["category"] != category:
            continue
            
        status_value = "completed" if step["id"] in current_user.completed_steps else "pending"
        
        if status and status_value != status:
            continue
            
        item = ProgressItem(
            id=str(step["id"]),
            title=step["title"],
            description=step["description"],
            status=status_value,
            category=step["category"],
            subtasks=[
                {"task": "Research requirements", "completed": status_value == "completed"},
                {"task": "Gather documents", "completed": status_value == "completed"},
                {"task": "Complete action", "completed": status_value == "completed"}
            ],
            notes=f"Timeline step {step['id']} - {step.get('estimated_days', 7)} days estimated"
        )
        items.append(item.dict())
    
    return {"items": items}

@api_router.put("/progress/items/{item_id}")
async def update_progress_item(item_id: str, current_user: User = Depends(get_current_user), status: Optional[str] = None, notes: Optional[str] = None):
    # Update step completion status
    step_id = int(item_id)
    user_completed_steps = current_user.completed_steps.copy()
    
    if status == "completed" and step_id not in user_completed_steps:
        user_completed_steps.append(step_id)
    elif status == "pending" and step_id in user_completed_steps:
        user_completed_steps.remove(step_id)
    
    # Update user in database
    await db.users.update_one(
        {"username": current_user.username},
        {"$set": {"completed_steps": user_completed_steps}}
    )
    
    return {"message": "Progress item updated successfully"}

@api_router.post("/progress/items/{item_id}/subtasks/{subtask_index}/toggle")
async def toggle_subtask(item_id: str, subtask_index: int, current_user: User = Depends(get_current_user)):
    # For now, just return success - subtasks are auto-completed based on main task status
    return {"message": "Subtask toggled successfully"}

# Logistics providers endpoints
@api_router.get("/logistics/providers")
async def get_logistics_providers():
    providers = [
        {
            "id": "crown001",
            "name": "Crown Relocations",
            "type": "Premium Moving Services",
            "description": "Full-service international relocation with door-to-door delivery",
            "services": ["Packing", "Shipping", "Storage", "Customs", "Insurance"],
            "coverage": "Worldwide",
            "estimated_cost": "$8,000 - $15,000",
            "timeline": "6-8 weeks",
            "contact": "crown@relocations.com",
            "phone": "+1-800-CROWN-US",
            "website": "https://www.crownrelo.com"
        },
        {
            "id": "allied002", 
            "name": "Allied International",
            "type": "Comprehensive Moving",
            "description": "Established moving company with UK expertise",
            "services": ["Household goods", "Vehicle shipping", "Pet relocation", "Storage"],
            "coverage": "US to UK specialized",
            "estimated_cost": "$6,000 - $12,000",
            "timeline": "4-6 weeks",
            "contact": "international@allied.com",
            "phone": "+1-800-ALLIED-1",
            "website": "https://www.allied.com"
        },
        {
            "id": "seven003",
            "name": "Seven Seas Worldwide", 
            "type": "Container Shipping",
            "description": "Flexible shipping options with shared and dedicated containers",
            "services": ["Shared containers", "Dedicated containers", "Port to port", "Door to door"],
            "coverage": "US to UK ports",
            "estimated_cost": "$3,000 - $8,000",
            "timeline": "3-5 weeks",
            "contact": "usa@sevenseas.com",
            "phone": "+1-800-SEA-MOVE",
            "website": "https://www.sevenseasworldwide.com"
        },
        {
            "id": "fedex004",
            "name": "FedEx International",
            "type": "Express Shipping",
            "description": "Fast shipping for smaller items and documents",
            "services": ["Express delivery", "Customs clearance", "Tracking", "Insurance"],
            "coverage": "Express worldwide",
            "estimated_cost": "$500 - $2,000",
            "timeline": "3-7 days",
            "contact": "international@fedex.com",
            "phone": "+1-800-FEDEX-GO",
            "website": "https://www.fedex.com"
        },
        {
            "id": "mybag005",
            "name": "My Baggage",
            "type": "Luggage Shipping",
            "description": "Affordable shipping for suitcases and boxes",
            "services": ["Luggage shipping", "Box shipping", "Student shipping", "Excess baggage"],
            "coverage": "US to UK budget friendly",
            "estimated_cost": "$200 - $1,000",
            "timeline": "5-10 days",
            "contact": "support@mybaggage.com",
            "phone": "+44-800-MY-BAGGAGE",
            "website": "https://www.mybaggage.com"
        },
        {
            "id": "shipsmrt006",
            "name": "Ship Smart",
            "type": "Container Shipping",
            "description": "Self-pack container service with flexible timing",
            "services": ["Self-pack containers", "Professional packing", "Storage", "Delivery"],
            "coverage": "Major US to UK routes",
            "estimated_cost": "$4,000 - $9,000",
            "timeline": "4-7 weeks",
            "contact": "info@shipsmart.com",
            "phone": "+1-866-SHIP-SMART",
            "website": "https://www.shipsmart.com"
        }
    ]
    
    return {"providers": providers}

# Include API router in main app
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "RelocateMe API v2.6 - Phoenix to Peak District Relocation Platform"}

# Startup event
@app.on_event("startup")
async def startup_event():
    await create_default_user()
    print("RelocateMe API started successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)