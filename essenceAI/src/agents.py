"""
Multi-Agent System for essenceAI
Provides specialized agents for different tasks with coordination capabilities
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod

# Import existing modules
from blackbox_client import BlackboxAIClient
from competitor_data import OptimizedCompetitorIntelligence
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTask:
    """Represents a task for an agent to execute."""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        priority: int = 5
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.parameters = parameters
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.logs = []

    def add_log(self, message: str):
        """Add log entry to task."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        logger.info(f"Task {self.task_id}: {message}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'description': self.description,
            'parameters': self.parameters,
            'priority': self.priority,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'logs': self.logs
        }


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.is_busy = False
        self.current_task = None
        logger.info(f"Agent initialized: {self.name} ({self.agent_id})")

    @abstractmethod
    def can_handle(self, task: AgentTask) -> bool:
        """Check if agent can handle the given task."""
        pass

    @abstractmethod
    def execute(self, task: AgentTask) -> Any:
        """Execute the task and return result."""
        pass

    def run_task(self, task: AgentTask) -> AgentTask:
        """
        Run a task with error handling and status tracking.

        Args:
            task: Task to execute

        Returns:
            Updated task with result or error
        """
        if not self.can_handle(task):
            task.status = TaskStatus.FAILED
            task.error = f"Agent {self.name} cannot handle task type: {task.task_type}"
            task.add_log(f"Task rejected: {task.error}")
            return task

        self.is_busy = True
        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.add_log(f"Task started by agent: {self.name}")

        try:
            # Execute the task
            result = self.execute(task)

            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            task.add_log("Task completed successfully")

            self.tasks_completed += 1

        except Exception as e:
            # Handle errors
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            task.add_log(f"Task failed: {str(e)}")

            self.tasks_failed += 1
            logger.error(f"Agent {self.name} task failed: {e}", exc_info=True)

        finally:
            self.is_busy = False
            self.current_task = None

        return task

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'is_busy': self.is_busy,
            'current_task': self.current_task.task_id if self.current_task else None
        }


class CompetitorAgent(BaseAgent):
    """
    Agent specialized in competitor research and analysis.
    Uses the existing OptimizedCompetitorIntelligence module.
    """

    def __init__(self):
        super().__init__("competitor-agent-001", "Competitor Research Agent")
        self.competitor_intel = OptimizedCompetitorIntelligence()

    def can_handle(self, task: AgentTask) -> bool:
        """Check if task is competitor-related."""
        return task.task_type in [
            "competitor_research",
            "market_analysis",
            "pricing_analysis",
            "competitor_comparison"
        ]

    def execute(self, task: AgentTask) -> Any:
        """Execute competitor research task."""
        task_type = task.task_type
        params = task.parameters

        if task_type == "competitor_research":
            return self._research_competitors(task, params)
        elif task_type == "market_analysis":
            return self._analyze_market(task, params)
        elif task_type == "pricing_analysis":
            return self._analyze_pricing(task, params)
        elif task_type == "competitor_comparison":
            return self._compare_competitors(task, params)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _research_competitors(self, task: AgentTask, params: Dict) -> Dict:
        """Research competitors for a product concept."""
        task.add_log("Fetching competitor data...")

        product_concept = params.get('product_concept', '')
        category = params.get('category')  # Don't default to 'Plant-Based'
        max_results = params.get('max_results', 10)

        competitors = self.competitor_intel.get_competitors(
            product_concept=product_concept,
            category=category,
            max_results=max_results,
            use_cache=True
        )

        task.add_log(f"Found {len(competitors)} competitors")

        return {
            'competitors': competitors,
            'count': len(competitors),
            'category': category
        }

    def _analyze_market(self, task: AgentTask, params: Dict) -> Dict:
        """Analyze market landscape."""
        task.add_log("Analyzing market landscape...")

        # Get competitors first
        competitors = self._research_competitors(task, params)['competitors']

        if not competitors:
            return {'error': 'No competitor data available'}

        # Calculate market statistics with error handling for empty data
        prices = [c.get('Price (€/kg)', 0) for c in competitors if c.get('Price (€/kg)') is not None]
        co2_values = [c.get('CO₂ (kg)', 0) for c in competitors if c.get('CO₂ (kg)') is not None]

        if not prices or not co2_values:
            return {'error': 'Competitor data is incomplete - missing price or CO2 information'}

        analysis = {
            'market_size': len(competitors),
            'price_stats': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) / len(prices) if prices else 0
            },
            'sustainability_stats': {
                'min_co2': min(co2_values) if co2_values else 0,
                'max_co2': max(co2_values) if co2_values else 0,
                'avg_co2': sum(co2_values) / len(co2_values) if co2_values else 0
            },
            'top_competitors': competitors[:5],
            'market_insights': self._generate_insights(competitors)
        }

        task.add_log("Market analysis completed")
        return analysis

    def _analyze_pricing(self, task: AgentTask, params: Dict) -> Dict:
        """Analyze pricing strategies."""
        task.add_log("Analyzing pricing strategies...")

        competitors = self._research_competitors(task, params)['competitors']

        if not competitors:
            return {'error': 'No competitor data available'}

        # Group by price ranges
        price_ranges = {
            'budget': [],
            'mid_range': [],
            'premium': []
        }

        for comp in competitors:
            price = comp.get('Price (€/kg)')
            # Handle None values - skip competitors without price data
            if price is None:
                continue

            if price < 20:
                price_ranges['budget'].append(comp)
            elif price < 40:
                price_ranges['mid_range'].append(comp)
            else:
                price_ranges['premium'].append(comp)

        # Check if we have any valid pricing data
        total_with_prices = sum(len(v) for v in price_ranges.values())
        if total_with_prices == 0:
            return {'error': 'No valid pricing data available for analysis'}

        analysis = {
            'price_segments': {
                'budget': {
                    'count': len(price_ranges['budget']),
                    'range': '< €20/kg',
                    'competitors': price_ranges['budget']
                },
                'mid_range': {
                    'count': len(price_ranges['mid_range']),
                    'range': '€20-40/kg',
                    'competitors': price_ranges['mid_range']
                },
                'premium': {
                    'count': len(price_ranges['premium']),
                    'range': '> €40/kg',
                    'competitors': price_ranges['premium']
                }
            },
            'pricing_strategy_recommendation': self._recommend_pricing(price_ranges)
        }

        task.add_log("Pricing analysis completed")
        return analysis

    def _compare_competitors(self, task: AgentTask, params: Dict) -> Dict:
        """Compare specific competitors."""
        task.add_log("Comparing competitors...")

        competitor_names = params.get('competitor_names', [])
        category = params.get('category', 'Plant-Based')

        # Get all competitors
        all_competitors = self.competitor_intel.get_competitors(
            product_concept=params.get('product_concept', ''),
            category=category,
            max_results=20,
            use_cache=True
        )

        # Filter to requested competitors
        selected = [c for c in all_competitors if c.get('Company') in competitor_names]

        comparison = {
            'competitors': selected,
            'comparison_matrix': self._create_comparison_matrix(selected)
        }

        task.add_log(f"Compared {len(selected)} competitors")
        return comparison

    def _generate_insights(self, competitors: List[Dict]) -> List[str]:
        """Generate market insights from competitor data."""
        insights = []

        if not competitors:
            return ["No competitor data available for insights"]

        # Price insights - filter out None values
        prices = [c.get('Price (€/kg)') for c in competitors if c.get('Price (€/kg)') is not None]
        if prices:
            avg_price = sum(prices) / len(prices)
            insights.append(f"Average market price: €{avg_price:.2f}/kg")

            if max(prices) / min(prices) > 2:
                insights.append("High price variance indicates diverse market segments")

        # Sustainability insights - filter out None values
        co2_values = [c.get('CO₂ (kg)') for c in competitors if c.get('CO₂ (kg)') is not None]
        if co2_values:
            avg_co2 = sum(co2_values) / len(co2_values)
            insights.append(f"Average CO₂ footprint: {avg_co2:.2f} kg/kg product")

        # Marketing claims analysis
        claims = [c.get('Marketing Claim', '') for c in competitors if c.get('Marketing Claim')]
        if claims:
            common_themes = self._extract_common_themes(claims)
            insights.append(f"Common marketing themes: {', '.join(common_themes[:3])}")

        return insights

    def _extract_common_themes(self, claims: List[str]) -> List[str]:
        """Extract common themes from marketing claims."""
        themes = []
        keywords = ['sustainable', 'natural', 'organic', 'plant-based', 'healthy', 'protein', 'taste']

        for keyword in keywords:
            count = sum(1 for claim in claims if keyword.lower() in claim.lower())
            if count > 0:
                themes.append(f"{keyword} ({count})")

        return themes

    def _recommend_pricing(self, price_ranges: Dict) -> str:
        """Recommend pricing strategy based on market analysis."""
        total = sum(len(v) for v in price_ranges.values())

        if not total:
            return "Insufficient data for pricing recommendation"

        # Calculate distribution
        budget_pct = len(price_ranges['budget']) / total * 100
        mid_pct = len(price_ranges['mid_range']) / total * 100
        premium_pct = len(price_ranges['premium']) / total * 100

        if mid_pct > 50:
            return "Market is dominated by mid-range products. Consider competitive pricing in €20-40/kg range."
        elif premium_pct > 40:
            return "Strong premium segment. Consider premium positioning if product quality justifies it."
        else:
            return "Diverse market. Consider value-based pricing strategy targeting specific segments."

    def _create_comparison_matrix(self, competitors: List[Dict]) -> Dict:
        """Create comparison matrix for competitors."""
        if not competitors:
            return {}

        matrix = {
            'companies': [c.get('Company') for c in competitors],
            'prices': [c.get('Price (€/kg)') for c in competitors],
            'co2_emissions': [c.get('CO₂ (kg)') for c in competitors],
            'marketing_claims': [c.get('Marketing Claim') for c in competitors]
        }

        return matrix


class CodeAgent(BaseAgent):
    """
    Agent specialized in code generation and technical tasks.
    Uses Blackbox AI for code-related operations.
    """

    def __init__(self):
        super().__init__("code-agent-001", "Code Generation Agent")
        self.blackbox_client = BlackboxAIClient()

    def can_handle(self, task: AgentTask) -> bool:
        """Check if task is code-related."""
        return task.task_type in [
            "generate_code",
            "analyze_code",
            "optimize_code",
            "debug_code",
            "data_processing"
        ]

    def execute(self, task: AgentTask) -> Any:
        """Execute code-related task."""
        task_type = task.task_type
        params = task.parameters

        if task_type == "generate_code":
            return self._generate_code(task, params)
        elif task_type == "analyze_code":
            return self._analyze_code(task, params)
        elif task_type == "optimize_code":
            return self._optimize_code(task, params)
        elif task_type == "debug_code":
            return self._debug_code(task, params)
        elif task_type == "data_processing":
            return self._process_data(task, params)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _generate_code(self, task: AgentTask, params: Dict) -> Dict:
        """Generate code based on requirements."""
        task.add_log("Generating code with Blackbox AI...")

        prompt = params.get('prompt', '')
        language = params.get('language', 'python')

        if not prompt:
            raise ValueError("Code generation requires 'prompt' parameter")

        code = self.blackbox_client.generate_code(
            prompt=prompt,
            language=language,
            use_cache=True
        )

        task.add_log(f"Generated {len(code)} characters of {language} code")

        return {
            'code': code,
            'language': language,
            'prompt': prompt
        }

    def _analyze_code(self, task: AgentTask, params: Dict) -> Dict:
        """Analyze existing code."""
        task.add_log("Analyzing code with Blackbox AI...")

        code = params.get('code', '')
        analysis_type = params.get('analysis_type', 'review')

        if not code:
            raise ValueError("Code analysis requires 'code' parameter")

        analysis = self.blackbox_client.analyze_code(
            code=code,
            task=analysis_type,
            use_cache=True
        )

        task.add_log("Code analysis completed")

        return {
            'analysis': analysis,
            'analysis_type': analysis_type,
            'code_length': len(code)
        }

    def _optimize_code(self, task: AgentTask, params: Dict) -> Dict:
        """Optimize existing code."""
        task.add_log("Optimizing code...")

        code = params.get('code', '')

        if not code:
            raise ValueError("Code optimization requires 'code' parameter")

        # First analyze for optimization opportunities
        analysis = self.blackbox_client.analyze_code(
            code=code,
            task="optimize",
            use_cache=True
        )

        task.add_log("Optimization suggestions generated")

        return {
            'original_code': code,
            'optimization_suggestions': analysis,
            'code_length': len(code)
        }

    def _debug_code(self, task: AgentTask, params: Dict) -> Dict:
        """Debug code and identify issues."""
        task.add_log("Debugging code...")

        code = params.get('code', '')
        error_message = params.get('error_message', '')

        if not code:
            raise ValueError("Code debugging requires 'code' parameter")

        debug_prompt = f"debug\n\nError: {error_message}" if error_message else "debug"

        debug_analysis = self.blackbox_client.analyze_code(
            code=code,
            task=debug_prompt,
            use_cache=True
        )

        task.add_log("Debug analysis completed")

        return {
            'code': code,
            'error_message': error_message,
            'debug_analysis': debug_analysis
        }

    def _process_data(self, task: AgentTask, params: Dict) -> Dict:
        """Process data using Blackbox AI."""
        task.add_log("Processing data...")

        data = params.get('data')
        processing_task = params.get('task', 'Analyze this data')

        if data is None:
            raise ValueError("Data processing requires 'data' parameter")

        result = self.blackbox_client.process_data(
            data=data,
            task=processing_task,
            use_cache=True
        )

        task.add_log("Data processing completed")

        return {
            'original_data': data,
            'processing_task': processing_task,
            'result': result
        }


class QualityAgent(BaseAgent):
    """
    Agent specialized in code quality checking and logging analysis.
    Uses Blackbox AI to detect mistakes, bugs, and quality issues.
    """

    def __init__(self):
        super().__init__("quality-agent-001", "Quality Assurance Agent")
        self.blackbox_client = BlackboxAIClient()

    def can_handle(self, task: AgentTask) -> bool:
        """Check if task is quality-related."""
        return task.task_type in [
            "check_code_quality",
            "find_bugs",
            "analyze_logs",
            "security_audit",
            "performance_audit"
        ]

    def execute(self, task: AgentTask) -> Any:
        """Execute quality assurance task."""
        task_type = task.task_type
        params = task.parameters

        if task_type == "check_code_quality":
            return self._check_code_quality(task, params)
        elif task_type == "find_bugs":
            return self._find_bugs(task, params)
        elif task_type == "analyze_logs":
            return self._analyze_logs(task, params)
        elif task_type == "security_audit":
            return self._security_audit(task, params)
        elif task_type == "performance_audit":
            return self._performance_audit(task, params)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _check_code_quality(self, task: AgentTask, params: Dict) -> Dict:
        """Check code quality and identify issues."""
        task.add_log("Checking code quality...")

        code = params.get('code', '')
        language = params.get('language', 'python')

        if not code:
            raise ValueError("Code quality check requires 'code' parameter")

        # Use Blackbox AI for comprehensive quality analysis
        prompt = f"""Analyze this {language} code for quality issues:

```{language}
{code}
```

Provide a detailed quality report including:
1. **Code Smells**: Identify bad practices, code smells, and anti-patterns
2. **Bugs**: Potential bugs or logical errors
3. **Security Issues**: Security vulnerabilities or risks
4. **Performance Issues**: Performance bottlenecks or inefficiencies
5. **Maintainability**: Code readability and maintainability concerns
6. **Best Practices**: Violations of language-specific best practices
7. **Recommendations**: Specific fixes and improvements

Format as JSON:
{{
  "overall_score": 0-100,
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "category": "bug|security|performance|style|maintainability",
      "line": line_number,
      "description": "issue description",
      "recommendation": "how to fix"
    }}
  ],
  "summary": "overall assessment"
}}"""

        messages = [
            {"role": "system", "content": "You are an expert code quality analyst. Provide thorough, actionable feedback."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.blackbox_client.chat_completion(
                messages=messages,
                model="blackbox-code",
                temperature=0.1,
                use_cache=True
            )

            content = response['choices'][0]['message']['content']

            # Try to parse JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            try:
                quality_report = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw analysis
                quality_report = {
                    "overall_score": None,
                    "issues": [],
                    "summary": content,
                    "raw_analysis": content
                }

            # Categorize issues by severity
            critical_issues = [i for i in quality_report.get('issues', []) if i.get('severity') == 'critical']
            high_issues = [i for i in quality_report.get('issues', []) if i.get('severity') == 'high']

            task.add_log(f"Found {len(quality_report.get('issues', []))} issues")
            task.add_log(f"Critical: {len(critical_issues)}, High: {len(high_issues)}")

            return {
                'quality_report': quality_report,
                'code_length': len(code),
                'language': language,
                'total_issues': len(quality_report.get('issues', [])),
                'critical_issues': len(critical_issues),
                'high_issues': len(high_issues)
            }

        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            raise

    def _find_bugs(self, task: AgentTask, params: Dict) -> Dict:
        """Find potential bugs in code."""
        task.add_log("Searching for bugs...")

        code = params.get('code', '')
        context = params.get('context', '')

        if not code:
            raise ValueError("Bug detection requires 'code' parameter")

        prompt = f"""Analyze this code for bugs and logical errors:

```
{code}
```

{f'Context: {context}' if context else ''}

Identify:
1. Logical errors
2. Runtime errors (null pointers, index out of bounds, etc.)
3. Edge cases not handled
4. Type mismatches
5. Resource leaks
6. Race conditions (if applicable)

For each bug found, provide:
- Line number
- Bug description
- Why it's a problem
- How to fix it
- Test case to reproduce (if applicable)"""

        messages = [
            {"role": "system", "content": "You are an expert bug hunter. Find all potential bugs."},
            {"role": "user", "content": prompt}
        ]

        response = self.blackbox_client.chat_completion(
            messages=messages,
            model="blackbox-code",
            temperature=0.1,
            use_cache=True
        )

        bug_analysis = response['choices'][0]['message']['content']

        task.add_log("Bug analysis completed")

        return {
            'code': code,
            'bug_analysis': bug_analysis,
            'has_context': bool(context)
        }

    def _analyze_logs(self, task: AgentTask, params: Dict) -> Dict:
        """Analyze log files for errors and issues."""
        task.add_log("Analyzing logs...")

        logs = params.get('logs', '')
        log_file = params.get('log_file', '')

        # Read log file if provided
        if log_file and not logs:
            try:
                with open(log_file, 'r') as f:
                    logs = f.read()
                task.add_log(f"Read {len(logs)} characters from {log_file}")
            except Exception as e:
                raise ValueError(f"Failed to read log file: {e}")

        if not logs:
            raise ValueError("Log analysis requires 'logs' or 'log_file' parameter")

        # Limit log size for API
        max_log_size = 10000
        if len(logs) > max_log_size:
            task.add_log(f"Truncating logs from {len(logs)} to {max_log_size} characters")
            logs = logs[-max_log_size:]  # Take last N characters (most recent)

        prompt = f"""Analyze these application logs for issues:

```
{logs}
```

Provide:
1. **Errors Found**: List all errors with timestamps
2. **Warnings**: Important warnings that need attention
3. **Patterns**: Recurring issues or patterns
4. **Root Causes**: Likely root causes of errors
5. **Recommendations**: How to fix the issues
6. **Severity Assessment**: Critical, High, Medium, Low

Summarize the health of the application based on these logs."""

        messages = [
            {"role": "system", "content": "You are a log analysis expert. Identify issues and patterns."},
            {"role": "user", "content": prompt}
        ]

        response = self.blackbox_client.chat_completion(
            messages=messages,
            model="blackbox",
            temperature=0.1,
            use_cache=True
        )

        log_analysis = response['choices'][0]['message']['content']

        task.add_log("Log analysis completed")

        return {
            'log_analysis': log_analysis,
            'log_size': len(logs),
            'log_file': log_file if log_file else 'inline'
        }

    def _security_audit(self, task: AgentTask, params: Dict) -> Dict:
        """Perform security audit on code."""
        task.add_log("Performing security audit...")

        code = params.get('code', '')
        language = params.get('language', 'python')

        if not code:
            raise ValueError("Security audit requires 'code' parameter")

        prompt = f"""Perform a security audit on this {language} code:

```{language}
{code}
```

Check for:
1. **Injection vulnerabilities** (SQL, command, XSS, etc.)
2. **Authentication/Authorization issues**
3. **Sensitive data exposure**
4. **Insecure dependencies**
5. **Cryptographic issues**
6. **Input validation problems**
7. **API security issues**
8. **Configuration issues**

For each vulnerability:
- Severity (Critical/High/Medium/Low)
- OWASP category (if applicable)
- Description
- Exploitation scenario
- Remediation steps"""

        messages = [
            {"role": "system", "content": "You are a security expert. Identify all security vulnerabilities."},
            {"role": "user", "content": prompt}
        ]

        response = self.blackbox_client.chat_completion(
            messages=messages,
            model="blackbox-code",
            temperature=0.1,
            use_cache=True
        )

        security_report = response['choices'][0]['message']['content']

        task.add_log("Security audit completed")

        return {
            'security_report': security_report,
            'code_length': len(code),
            'language': language
        }

    def _performance_audit(self, task: AgentTask, params: Dict) -> Dict:
        """Audit code for performance issues."""
        task.add_log("Auditing performance...")

        code = params.get('code', '')
        language = params.get('language', 'python')

        if not code:
            raise ValueError("Performance audit requires 'code' parameter")

        prompt = f"""Analyze this {language} code for performance issues:

```{language}
{code}
```

Identify:
1. **Algorithmic complexity issues** (O(n²) where O(n) possible, etc.)
2. **Memory inefficiencies** (unnecessary copies, leaks, etc.)
3. **Database query issues** (N+1 queries, missing indexes, etc.)
4. **Network inefficiencies** (unnecessary requests, no caching, etc.)
5. **CPU-intensive operations** (in hot paths)
6. **I/O bottlenecks**
7. **Concurrency issues**

For each issue:
- Location in code
- Current complexity/performance
- Optimization suggestion
- Expected improvement"""

        messages = [
            {"role": "system", "content": "You are a performance optimization expert."},
            {"role": "user", "content": prompt}
        ]

        response = self.blackbox_client.chat_completion(
            messages=messages,
            model="blackbox-code",
            temperature=0.1,
            use_cache=True
        )

        performance_report = response['choices'][0]['message']['content']

        task.add_log("Performance audit completed")

        return {
            'performance_report': performance_report,
            'code_length': len(code),
            'language': language
        }


class AgentManager:
    """
    Manages multiple agents and coordinates task execution.
    """

    def __init__(self):
        self.agents: List[BaseAgent] = []
        self.tasks: Dict[str, AgentTask] = {}
        self.task_counter = 0

        # Initialize default agents
        self._initialize_agents()

        logger.info("AgentManager initialized")

    def _initialize_agents(self):
        """Initialize default agents."""
        self.agents.append(CompetitorAgent())
        self.agents.append(CodeAgent())
        self.agents.append(QualityAgent())
        logger.info(f"Initialized {len(self.agents)} agents")

    def create_task(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        priority: int = 5
    ) -> AgentTask:
        """
        Create a new task.

        Args:
            task_type: Type of task
            description: Task description
            parameters: Task parameters
            priority: Task priority (1-10, higher = more important)

        Returns:
            Created task
        """
        self.task_counter += 1
        task_id = f"task-{self.task_counter:04d}"

        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            parameters=parameters,
            priority=priority
        )

        self.tasks[task_id] = task
        logger.info(f"Task created: {task_id} ({task_type})")

        return task

    def execute_task(self, task_id: str) -> AgentTask:
        """
        Execute a task by finding appropriate agent.

        Args:
            task_id: Task ID to execute

        Returns:
            Completed task
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")

        task = self.tasks[task_id]

        # Find agent that can handle this task
        for agent in self.agents:
            if agent.can_handle(task) and not agent.is_busy:
                logger.info(f"Assigning task {task_id} to agent {agent.name}")
                return agent.run_task(task)

        # No available agent
        task.status = TaskStatus.FAILED
        task.error = "No available agent can handle this task"
        logger.warning(f"No agent available for task {task_id}")

        return task

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[AgentTask]:
        """Get all tasks."""
        return list(self.tasks.values())

    def get_agent_stats(self) -> List[Dict]:
        """Get statistics for all agents."""
        return [agent.get_stats() for agent in self.agents]

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)

        return {
            'total_agents': len(self.agents),
            'total_tasks': total_tasks,
            'tasks_completed': completed,
            'tasks_failed': failed,
            'tasks_running': running,
            'tasks_pending': pending,
            'agents': self.get_agent_stats()
        }


# Global agent manager instance
_agent_manager = None


def get_agent_manager() -> AgentManager:
    """Get global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager
