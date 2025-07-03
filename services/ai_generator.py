import re
import google.generativeai as genai
import markdown
import os
from bs4 import BeautifulSoup

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def enhance_prompt(raw_prompt):
    """Refine and enhance user's input prompt"""
    enhancement_prompt = f"""
    Please refine and enhance this business idea description for clarity and completeness. 
    Maintain the core concept but add relevant business context, clarify ambiguities, 
    and expand on key aspects while keeping it concise. Do not invent new features.
    
    Original idea: {raw_prompt}
    
    Enhanced version:
    """
    try:
        response = model.generate_content(enhancement_prompt)
        return response.text.strip()
    except Exception:
        return raw_prompt


def sanitize_markdown_tables(md):
    """
    Fix malformed markdown tables that are embedded inside list items.
    Converts lines like:
      - Table: | Col1 | Col2 | ...
    Into:
      - Table:
        | Col1 | Col2 | ...
    """
    fixed_lines = []
    for line in md.splitlines():
        if re.match(r"^\s*-\s+.*\|.*\|", line):
            parts = line.split("|")
            if len(parts) >= 3:
                prefix, rest = line.split("|", 1)
                if ":" in prefix or "Model" in prefix:
                    fixed_lines.append(prefix.strip() + ":")
                    fixed_lines.append("|" + rest.strip())
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)


def format_tables_with_bootstrap(html):
    """Add Bootstrap styling to all tables in the generated HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    for table in soup.find_all('table'):
        table['class'] = table.get('class', []) + ['table', 'table-bordered', 'table-striped', 'mt-4']
    return str(soup)


def generate_startup_plan(data):
    """Generate business plan using Gemini API"""
    enhanced_idea = enhance_prompt(data['startup_idea'])
    
    budget = data.get('budget')
    budget_text = f"${budget:,.0f}" if budget and budget > 0 else "Not specified"

    prompt = f"""
    Generate a structured startup plan for: {enhanced_idea}

    Budget: {budget_text}

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

    ## 💰 Budget Allocation
    - Proposed use of funds (development, marketing, operations)
    - Budget constraints considerations
    - Use a table with columns: Item, Allocation, Notes

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
        raw_markdown = sanitize_markdown_tables(response.text)
        html = markdown.markdown(raw_markdown, extensions=['markdown.extensions.tables'])
        styled_html = format_tables_with_bootstrap(html)
        return styled_html, raw_markdown, None
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
        raw_markdown = sanitize_markdown_tables(response.text)
        html = markdown.markdown(raw_markdown, extensions=['markdown.extensions.tables'])
        return format_tables_with_bootstrap(html), None
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
        raw_markdown = sanitize_markdown_tables(response.text)
        html = markdown.markdown(raw_markdown, extensions=['markdown.extensions.tables'])
        return format_tables_with_bootstrap(html), None
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
        raw_markdown = sanitize_markdown_tables(response.text)
        html = markdown.markdown(raw_markdown, extensions=['markdown.extensions.tables'])
        return format_tables_with_bootstrap(html), None
    except Exception as e:
        return None, str(e)
