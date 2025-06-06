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

# Extended 39-Step Relocation Timeline
RELOCATION_TIMELINE = [
    # Planning Phase (Days -180 to -90)
    {"id": 1, "title": "Initial Research & Decision", "description": "Research Peak District areas, cost of living, and lifestyle", "category": "Planning", "estimated_days": 7, "dependencies": [], "resources": ["Peak District National Park Authority", "UK Government Moving Guide"]},
    {"id": 2, "title": "Create Relocation Budget", "description": "Set aside $400k total budget - Calculate moving costs, visa fees, initial living expenses", "category": "Planning", "estimated_days": 3, "dependencies": [1], "resources": ["UK Cost Calculator", "Moving Cost Estimator"]},
    {"id": 3, "title": "Timeline & Milestones", "description": "Set target dates for visa, job search, housing, and moving", "category": "Planning", "estimated_days": 2, "dependencies": [2], "resources": ["Project Management Templates"]},
    {"id": 4, "title": "Skills Assessment for Hospitality", "description": "Evaluate hospitality/waitressing experience and UK requirements", "category": "Planning", "estimated_days": 3, "dependencies": [1], "resources": ["UK Hospitality Standards", "Skills Recognition"]},
    {"id": 5, "title": "Language Preparation", "description": "Assess English language skills and prepare for potential testing", "category": "Planning", "estimated_days": 14, "dependencies": [4], "resources": ["IELTS Preparation", "English Language Centers"]},
    
    # Visa & Legal (Days -150 to -60)
    {"id": 6, "title": "Visa Research", "description": "Determine visa type needed (work, skilled worker, family, etc.)", "category": "Visa & Legal", "estimated_days": 5, "dependencies": [1], "resources": ["UK Government Visa Guide", "Immigration Lawyer Directory"]},
    {"id": 7, "title": "Document Preparation", "description": "Gather birth certificate, passport, education certificates, etc.", "category": "Visa & Legal", "estimated_days": 14, "dependencies": [6], "resources": ["Document Checklist", "Apostille Services"]},
    {"id": 8, "title": "Criminal Background Check", "description": "Obtain FBI background check and state-level clearances", "category": "Visa & Legal", "estimated_days": 21, "dependencies": [7], "resources": ["FBI Background Check", "State Police Records"]},
    {"id": 9, "title": "Medical Examinations", "description": "Complete required medical exams including TB testing", "category": "Visa & Legal", "estimated_days": 14, "dependencies": [8], "resources": ["Medical Exam Centers", "TB Testing Centers"]},
    {"id": 10, "title": "Visa Application Submission", "description": "Submit visa application with all required documents", "category": "Visa & Legal", "estimated_days": 21, "dependencies": [9], "resources": ["UK Visa Application Centre"]},
    {"id": 11, "title": "Biometric Appointment", "description": "Attend biometric appointment for fingerprints and photo", "category": "Visa & Legal", "estimated_days": 7, "dependencies": [10], "resources": ["VFS Global Centers"]},
    
    # Employment (Days -120 to -30)
    {"id": 12, "title": "Hospitality Job Market Research", "description": "Research waitressing and hospitality opportunities in Peak District", "category": "Employment", "estimated_days": 7, "dependencies": [1], "resources": ["UK Hospitality Jobs", "Peak District Restaurant Guide"]},
    {"id": 13, "title": "UK CV/Resume Creation", "description": "Adapt resume for UK hospitality standards and format", "category": "Employment", "estimated_days": 3, "dependencies": [12], "resources": ["UK CV Templates", "Hospitality CV Examples"]},
    {"id": 14, "title": "Professional References", "description": "Contact previous hospitality employers for UK-formatted references", "category": "Employment", "estimated_days": 7, "dependencies": [13], "resources": ["Reference Templates", "Professional Networks"]},
    {"id": 15, "title": "Hospitality Certification Review", "description": "Check if US food safety/hospitality certs transfer to UK", "category": "Employment", "estimated_days": 10, "dependencies": [14], "resources": ["UK Food Safety Training", "Hospitality Qualifications"]},
    {"id": 16, "title": "Peak District Job Applications", "description": "Apply for waitressing/hospitality positions in target area", "category": "Employment", "estimated_days": 30, "dependencies": [15], "resources": ["Restaurant Websites", "Hospitality Job Boards"]},
    {"id": 17, "title": "Video/Phone Interviews", "description": "Participate in remote interviews with Peak District employers", "category": "Employment", "estimated_days": 21, "dependencies": [16], "resources": ["Interview Preparation", "Video Call Setup"]},
    {"id": 18, "title": "Job Offer Negotiation", "description": "Negotiate salary, accommodation assistance, and start dates", "category": "Employment", "estimated_days": 14, "dependencies": [17], "resources": ["Salary Negotiation Guide", "Contract Review"]},
    
    # Housing (Days -90 to -14)
    {"id": 19, "title": "Peak District Housing Research", "description": "Research neighborhoods, property types, rental market in target area", "category": "Housing", "estimated_days": 14, "dependencies": [1], "resources": ["Rightmove", "Zoopla", "Local Estate Agents"]},
    {"id": 20, "title": "Virtual Property Viewings", "description": "Arrange virtual viewings of potential homes", "category": "Housing", "estimated_days": 21, "dependencies": [19], "resources": ["Property Viewing Apps", "Virtual Tour Platforms"]},
    {"id": 21, "title": "Rental Applications", "description": "Apply for rental properties with deposit and references", "category": "Housing", "estimated_days": 21, "dependencies": [20], "resources": ["Rental Application Forms", "Guarantor Services"]},
    {"id": 22, "title": "Housing Contract Finalization", "description": "Sign lease agreement and arrange initial payments", "category": "Housing", "estimated_days": 7, "dependencies": [21], "resources": ["Legal Services", "Property Lawyers"]},
    {"id": 23, "title": "Utility Setup Preparation", "description": "Research and prepare to set up utilities for new home", "category": "Housing", "estimated_days": 5, "dependencies": [22], "resources": ["Utility Companies", "Comparison Sites"]},
    
    # Financial (Days -60 to -7)
    {"id": 24, "title": "UK Bank Account Research", "description": "Research UK banks and account options for new residents", "category": "Financial", "estimated_days": 7, "dependencies": [10], "resources": ["Bank Comparison Sites", "Expat Banking Guide"]},
    {"id": 25, "title": "International Money Transfer Setup", "description": "Establish currency exchange and transfer services for $400k budget", "category": "Financial", "estimated_days": 10, "dependencies": [24], "resources": ["Wise", "Western Union", "CurrencyFair"]},
    {"id": 26, "title": "UK Bank Account Application", "description": "Apply for UK current and savings accounts", "category": "Financial", "estimated_days": 14, "dependencies": [25], "resources": ["Barclays", "HSBC", "Monzo", "Starling"]},
    {"id": 27, "title": "Insurance Research & Setup", "description": "Arrange health, contents, and travel insurance", "category": "Financial", "estimated_days": 7, "dependencies": [22], "resources": ["Insurance Brokers", "NHS Information"]},
    {"id": 28, "title": "Budget Transfer Planning", "description": "Plan transfer of $400k budget in stages for tax efficiency", "category": "Financial", "estimated_days": 5, "dependencies": [26], "resources": ["Tax Advisors", "Transfer Specialists"]},
    
    # Logistics (Days -30 to +7)
    {"id": 29, "title": "International Moving Quotes", "description": "Get quotes from international moving companies for household goods", "category": "Logistics", "estimated_days": 10, "dependencies": [22], "resources": ["International Movers", "Shipping Companies"]},
    {"id": 30, "title": "Moving Company Selection", "description": "Choose moving company and book services", "category": "Logistics", "estimated_days": 5, "dependencies": [29], "resources": ["Moving Contracts", "Insurance Options"]},
    {"id": 31, "title": "Flight and Travel Booking", "description": "Book flights and initial UK accommodation", "category": "Logistics", "estimated_days": 3, "dependencies": [10], "resources": ["Flight Booking Sites", "Temporary Accommodation"]},
    {"id": 32, "title": "Customs Documentation", "description": "Prepare customs forms and documentation for shipped goods", "category": "Logistics", "estimated_days": 7, "dependencies": [30], "resources": ["Customs Brokers", "HMRC Guidelines"]},
    {"id": 33, "title": "Packing and Shipping", "description": "Pack belongings and ship to UK", "category": "Logistics", "estimated_days": 7, "dependencies": [32], "resources": ["Packing Services", "Shipping Insurance"]},
    
    # US Exit Procedures (Days -14 to 0)
    {"id": 34, "title": "US Service Cancellations", "description": "Cancel utilities, subscriptions, and local services", "category": "US Exit", "estimated_days": 10, "dependencies": [31], "resources": ["Utility Companies", "Service Providers"]},
    {"id": 35, "title": "Address Change Notifications", "description": "Update address with IRS, banks, and government agencies", "category": "US Exit", "estimated_days": 7, "dependencies": [34], "resources": ["USPS Mail Forwarding", "IRS Forms"]},
    {"id": 36, "title": "Final US Tax Preparation", "description": "Prepare final US tax returns and plan for ongoing obligations", "category": "US Exit", "estimated_days": 5, "dependencies": [35], "resources": ["Tax Advisors", "Expat Tax Services"]},
    
    # UK Arrival (Days 1 to 30)
    {"id": 37, "title": "UK Border Entry", "description": "Arrive in UK and complete immigration procedures", "category": "UK Arrival", "estimated_days": 1, "dependencies": [36], "resources": ["UK Border Control", "Immigration Guidelines"]},
    {"id": 38, "title": "Temporary Accommodation Check-in", "description": "Check into temporary housing while awaiting permanent residence", "category": "UK Arrival", "estimated_days": 2, "dependencies": [37], "resources": ["Hotels", "Serviced Apartments"]},
    {"id": 39, "title": "Essential Registrations", "description": "Register with GP, council, and begin National Insurance application", "category": "UK Arrival", "estimated_days": 14, "dependencies": [38], "resources": ["NHS Registration", "Local Council", "HMRC"]}
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

# Enhanced Resources endpoints - All links for 39 steps
@api_router.get("/resources/all")
async def get_all_resources():
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