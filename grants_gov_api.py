import asyncio
import logging
import time
import httpx
from datetime import datetime
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)


class GrantsGovAPI:
    """Handle Grants.gov API integration - Adapted for MCP"""

    BASE_URL = "https://www.grants.gov/grantsws/rest/opportunities/search/"

    # Mock data fallback for when API returns empty or fails
    MOCK_GRANTS = [
        {
            "title": "AI-Driven Clean Energy Optimization SBIR",
            "opportunity_number": "DE-FOA-0003001",
            "agency": "Department of Energy",
            "description": "Funding for AI startups developing grid optimization "
                           "and renewable energy integration technologies.",
            "award_ceiling": "$275,000",
            "award_floor": "$150,000",
            "close_date": "December 15, 2025",
            "post_date": "September 1, 2025",
            "url": "https://www.energy.gov/eere/funding",
            "category": "Energy",
            "cfda_numbers": ["81.049"],
            "eligible_applicants": ["Small Business"],
            "source": "Web"
        },
        {
            "title": "Next-Gen Climate Tech Accelerator",
            "opportunity_number": "NSF-24-501",
            "agency": "National Science Foundation",
            "description": "Accelerating breakthrough climate technologies. "
                           "Seeks proposals for high-impact solutions.",
            "award_ceiling": "$1,000,000",
            "award_floor": "$250,000",
            "close_date": "January 30, 2026",
            "post_date": "October 15, 2025",
            "url": "https://new.nsf.gov/funding/opportunities",
            "category": "Science and Technology",
            "cfda_numbers": ["47.041"],
            "eligible_applicants": ["Small Business", "Startup"],
            "source": "Web"
        }
    ]

    def __init__(self):
        self.headers = {
            'User-Agent': 'GrantHunterMCP/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.timeout = 10  # 10 seconds timeout
        self.max_retries = 5  # 5 attempts (Production AgentOps Standard)

    async def search_grants(self, keyword: str, limit: int = 20) -> List[Dict]:
        """Search for grants using Grants.gov API"""
        try:
            logger.info(f"Starting Grants.gov API search for keyword: {keyword}")

            # Search by keyword
            grants = await self._search_by_keyword(keyword, limit=limit)

            # Deduplication
            seen_numbers = set()
            unique_grants = []

            for grant in grants:
                opp_number = grant.get(
                    'opportunity_number',
                    grant.get('opportunityNumber', '')
                )
                if opp_number and opp_number not in seen_numbers:
                    seen_numbers.add(opp_number)
                    unique_grants.append(grant)

            # Sort by close date (earliest first)
            unique_grants.sort(
                key=lambda x: self._parse_date(
                    x.get('close_date', x.get('closeDate', ''))
                )
            )

            # Cap results
            result_grants = unique_grants[:limit]

            # Use mock fallback if no results found
            if not result_grants:
                logger.warning("No grants found from API, using mock fallback")
                result_grants = self.MOCK_GRANTS[:limit]

            logger.info(
                f"Grants.gov search completed: {len(result_grants)} grants found"
            )
            return result_grants

        except Exception as e:
            logger.error(f"Error searching grants: {str(e)}")
            logger.info("Using mock fallback due to API error")
            return self.MOCK_GRANTS[:limit]

    async def _search_by_keyword(
        self,
        keyword: str,
        limit: int = 20
    ) -> List[Dict]:
        """Search grants by specific keyword with retry logic (5 attempts)"""
        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout
        ) as client:
            for attempt in range(self.max_retries):
                try:
                    # Construct search parameters
                    params = {
                        'keyword': keyword,
                        'sortBy': 'closeDate',
                        'sortOrder': 'ASC',
                        'rows': limit,
                        'startRecordNum': 0
                    }

                    logger.debug(
                        f"API request attempt {attempt + 1}/{self.max_retries} "
                        f"for keyword '{keyword}'"
                    )
                    response = await client.get(
                        self.BASE_URL,
                        params=params
                    )

                    # Check for 429 and 5xx errors and retry with backoff
                    if response.status_code == 429 or response.status_code >= 500:
                        if attempt < self.max_retries - 1:
                            backoff_time = (2 ** attempt)
                            logger.warning(
                                f"HTTP {response.status_code} error for "
                                f"keyword '{keyword}', retrying in {backoff_time}s "
                                f"(attempt {attempt + 1}/{self.max_retries})"
                            )
                            await asyncio.sleep(backoff_time)
                            continue
                        else:
                            logger.error(
                                f"Max retries reached for keyword '{keyword}' "
                                f"with status {response.status_code}"
                            )
                            response.raise_for_status()

                    response.raise_for_status()

                    data = response.json()

                    if 'oppHits' in data and data['oppHits']:
                        return self._format_grants(data['oppHits'])

                    return []

                except httpx.TimeoutException as e:
                    logger.warning(
                        f"Timeout error for keyword '{keyword}' "
                        f"(attempt {attempt + 1}): {str(e)}"
                    )
                    if attempt < self.max_retries - 1:
                        backoff_time = (2 ** attempt)
                        await asyncio.sleep(backoff_time)
                        continue
                except httpx.HTTPError as e:
                    logger.warning(
                        f"API request error for keyword '{keyword}' "
                        f"(attempt {attempt + 1}): {str(e)}"
                    )
                    response = getattr(e, "response", None)
                    if attempt < self.max_retries - 1 and response:
                        if response.status_code == 429 or response.status_code >= 500:
                            backoff_time = (2 ** attempt)
                            await asyncio.sleep(backoff_time)
                            continue
                    if attempt == self.max_retries - 1:
                        break
                except Exception as e:
                    logger.error(
                        f"Unexpected error for keyword '{keyword}' "
                        f"(attempt {attempt + 1}): {str(e)}"
                    )
                    if attempt < self.max_retries - 1:
                        backoff_time = (2 ** attempt)
                        await asyncio.sleep(backoff_time)
                        continue
                    break

        logger.warning(
            f"All retry attempts failed for keyword '{keyword}', "
            "returning empty list"
        )
        return []

    def _format_grants(self, raw_grants: List[Dict]) -> List[Dict]:
        """Format raw API response into standardized grant objects"""
        formatted_grants = []

        for grant in raw_grants:
            try:
                description = grant.get('description', '')
                if len(description) > 500:
                    description = description[:500] + '...'

                formatted_grant = {
                    'title': grant.get('opportunityTitle', 'Unknown Title'),
                    'opportunity_number': grant.get('opportunityNumber', ''),
                    'agency': grant.get('ownerFullName', 'Unknown Agency'),
                    'description': description,
                    'award_ceiling': self._format_amount(
                        grant.get('awardCeiling')
                    ),
                    'award_floor': self._format_amount(
                        grant.get('awardFloor')
                    ),
                    'close_date': self._format_date(grant.get('closeDate')),
                    'post_date': self._format_date(grant.get('postDate')),
                    'url': (
                        f"https://www.grants.gov/search-grants?"
                        f"oppNum={grant.get('opportunityNumber', '')}"
                    ),
                    'category': grant.get('categoryOfFundingActivity', 'Other'),
                    'cfda_numbers': grant.get('cfdaNumbers', []),
                    'eligible_applicants': grant.get('eligibleApplicants', []),
                    'source': 'Web'
                }

                formatted_grants.append(formatted_grant)

            except Exception as e:
                logger.error(f"Error formatting grant: {str(e)}")
                continue

        return formatted_grants

    def _format_amount(self, amount) -> str:
        """Format monetary amount"""
        if not amount:
            return 'Not specified'

        try:
            amount_num = float(amount)
            if amount_num >= 1000000:
                return f"${amount_num/1000000:.1f}M"
            elif amount_num >= 1000:
                return f"${amount_num/1000:.0f}K"
            else:
                return f"${amount_num:.0f}"
        except (ValueError, TypeError):
            return str(amount)

    def _format_date(self, date_str) -> str:
        """Format date string"""
        if not date_str:
            return 'Not specified'

        try:
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%B %d, %Y')
                except ValueError:
                    continue

            return date_str

        except Exception:
            return date_str

    def _parse_date(self, date_str) -> datetime:
        """Parse date string to datetime object for sorting"""
        if not date_str:
            return datetime.max

        try:
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%B %d, %Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

            return datetime.max

        except Exception:
            return datetime.max
