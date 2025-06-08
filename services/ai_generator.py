import google.generativeai as genai
import markdown
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_startup_plan(data):
    """Generate business plan using Gemini API"""
    prompt = f"""
    Generate a structured startup plan for: {data['startup_idea']}
    
    Follow this exact format:
    
    # 🚀 {data.get('startup_name', 'Startup')} AI Business Plan
    
    ## 🎯 Executive Summary
    - Concise overview of the business concept
    - Key objectives and vision
    
    ## 🔍 Problem Statement
    - Clear description of the problem being solved
    - Current market gaps
    
    ## 👥 Target Audience
    - Primary customer segments
    - Demographic/psychographic details
    - Pain points addressed
    
    ## 💡 Solution Overview
    - Core product/service description
    - Key features and capabilities
    
    ## 🌟 Unique Selling Point (USP)
    - Competitive differentiation
    - Value proposition
    
    ## 💰 Revenue Model
    - Monetization strategy
    - Pricing model options
    - Potential revenue streams
    
    ## 🛠 Suggested MVP
    - Minimum viable product components
    - Core functionality priorities
    - Validation metrics
    
    ## 🔧 Suggested Tech Stack
    - Recommended technologies
    - AI/ML tools
    - Infrastructure requirements
    
    ## ⏳ Timeline Snapshot
    ### 0-30 Days
    - Key milestones
    - Deliverables
    
    ### 31-60 Days
    - Development phases
    - Testing goals
    
    ### 61-90 Days
    - Launch preparations
    - Growth initiatives
    
    Use markdown formatting with:
    - Clear section headers (## level)
    - Bullet points for lists
    - Emoji icons for visual hierarchy
    - Bold key terms
    - Tables where appropriate
    """
    
    try:
        response = model.generate_content(prompt)
        raw_markdown = response.text  
        html_content = markdown.markdown(raw_markdown)  
        return html_content, raw_markdown, None  
    except Exception as e:
        return None, None, str(e)
    
def generate_market_research(idea):
    """Generate market research using Gemini API"""
    prompt = f"""
    Provide detailed market research for this startup idea: {idea}
    
    Include:
    - Current market size and growth projections
    - Top 3-5 competitors with analysis
    - Emerging industry trends
    - SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
    
    Use markdown formatting with bullet points and tables.
    """
    try:
        response = model.generate_content(prompt)
        return response.text, None 
    except Exception as e:
        return None, str(e)

def generate_tech_stack(idea):
    """Generate tech stack recommendations using Gemini API"""
    prompt = f"""
    Recommend a modern tech stack for this startup idea: {idea}
    
    Include:
    - Frontend frameworks
    - Backend technologies
    - Database solutions
    - AI/ML tools
    - Cloud infrastructure
    - DevOps tools
    
    Format as markdown with categories and bullet points.
    """
    try:
        response = model.generate_content(prompt)
        return response.text, None 
    except Exception as e:
        return None, str(e)

def generate_revenue_models(idea):
    """Generate revenue models using Gemini API"""
    prompt = f"""
    Suggest multiple revenue models for this startup idea: {idea}
    
    Include:
    - 3-5 monetization strategies
    - Pricing model comparisons
    - Subscription vs one-time purchase analysis
    - Potential partnership opportunities
    - Advertising strategies if applicable
    
    Use markdown tables and bullet points.
    """
    try:
        response = model.generate_content(prompt)
        return response.text, None 
    except Exception as e:
        return None, str(e)