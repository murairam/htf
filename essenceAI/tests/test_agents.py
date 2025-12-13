"""
Tests for the Agent System
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents import (
    BaseAgent,
    ResearchAgent,
    CompetitorAgent,
    MarketingAgent,
    AgentOrchestrator
)
from agents.agent_config import (
    AgentConfig,
    get_workflow_template,
    validate_task_params,
    get_agent_capabilities,
    WorkflowType
)


class TestBaseAgent:
    """Tests for BaseAgent class."""

    class ConcreteAgent(BaseAgent):
        """Concrete implementation for testing."""
        def execute(self, task):
            return self._create_success_response(task, "Test completed")

    def test_initialization(self):
        """Test agent initialization."""
        agent = self.ConcreteAgent("TestAgent", "Test description")
        assert agent.name == "TestAgent"
        assert agent.description == "Test description"
        assert len(agent.history) == 0

    def test_log_action(self):
        """Test action logging."""
        agent = self.ConcreteAgent("TestAgent", "Test description")
        agent.log_action("test_action", {"key": "value"})
        
        assert len(agent.history) == 1
        assert agent.history[0]['action'] == "test_action"
        assert agent.history[0]['details']['key'] == "value"

    def test_get_status(self):
        """Test status retrieval."""
        agent = self.ConcreteAgent("TestAgent", "Test description")
        status = agent.get_status()
        
        assert status['name'] == "TestAgent"
        assert status['description'] == "Test description"
        assert status['actions_count'] == 0

    def test_clear_history(self):
        """Test history clearing."""
        agent = self.ConcreteAgent("TestAgent", "Test description")
        agent.log_action("test", {})
        assert len(agent.history) == 1
        
        agent.clear_history()
        assert len(agent.history) == 0

    def test_success_response(self):
        """Test success response creation."""
        agent = self.ConcreteAgent("TestAgent", "Test description")
        response = agent._create_success_response({"data": "test"}, "Success")
        
        assert response['status'] == 'success'
        assert response['agent'] == "TestAgent"
        assert response['message'] == "Success"
        assert response['data']['data'] == "test"

    def test_error_response(self):
        """Test error response creation."""
        agent = self.ConcreteAgent("TestAgent", "Test description")
        response = agent._create_error_response("Error occurred", {"detail": "info"})
        
        assert response['status'] == 'error'
        assert response['agent'] == "TestAgent"
        assert response['error'] == "Error occurred"
        assert response['details']['detail'] == "info"


class TestMarketingAgent:
    """Tests for MarketingAgent."""

    def test_initialization(self):
        """Test marketing agent initialization."""
        agent = MarketingAgent()
        assert agent.name == "MarketingAgent"
        assert len(agent.SEGMENT_PROFILES) == 3

    def test_execute_success(self):
        """Test successful strategy generation."""
        agent = MarketingAgent()
        result = agent.execute({
            'product_description': 'Test product',
            'segment': 'High Essentialist',
            'domain': 'Plant-Based'
        })
        
        assert result['status'] == 'success'
        assert 'data' in result
        assert result['data']['segment'] == 'High Essentialist'
        assert 'positioning' in result['data']
        assert 'messaging' in result['data']

    def test_execute_missing_product(self):
        """Test execution with missing product description."""
        agent = MarketingAgent()
        result = agent.execute({
            'segment': 'High Essentialist'
        })
        
        assert result['status'] == 'error'
        assert 'product_description' in result['error']

    def test_execute_missing_segment(self):
        """Test execution with missing segment."""
        agent = MarketingAgent()
        result = agent.execute({
            'product_description': 'Test product'
        })
        
        assert result['status'] == 'error'
        assert 'segment' in result['error']

    def test_execute_invalid_segment(self):
        """Test execution with invalid segment."""
        agent = MarketingAgent()
        result = agent.execute({
            'product_description': 'Test product',
            'segment': 'Invalid Segment'
        })
        
        assert result['status'] == 'error'
        assert 'Unknown segment' in result['error']

    def test_get_segment_profiles(self):
        """Test segment profile retrieval."""
        agent = MarketingAgent()
        profiles = agent.get_segment_profiles()
        
        assert len(profiles) == 3
        assert 'High Essentialist' in profiles
        assert 'Skeptic' in profiles
        assert 'Non-Consumer' in profiles

    def test_compare_segments(self):
        """Test segment comparison."""
        agent = MarketingAgent()
        result = agent.compare_segments('Test product', 'Plant-Based')
        
        assert result['status'] == 'success'
        assert len(result['data']) == 3
        assert 'High Essentialist' in result['data']


class TestCompetitorAgent:
    """Tests for CompetitorAgent."""

    def test_initialization(self):
        """Test competitor agent initialization."""
        agent = CompetitorAgent()
        assert agent.name == "CompetitorAgent"
        assert agent.intelligence is not None

    @patch('agents.competitor_agent.CompetitorIntelligence')
    def test_execute_success(self, mock_intelligence):
        """Test successful competitor analysis."""
        # Mock the competitor intelligence
        mock_instance = Mock()
        mock_instance.get_competitors.return_value = [
            {'name': 'Competitor 1', 'price_usd': 10.0, 'co2_kg_per_kg': 2.5},
            {'name': 'Competitor 2', 'price_usd': 15.0, 'co2_kg_per_kg': 3.0}
        ]
        mock_intelligence.return_value = mock_instance
        
        agent = CompetitorAgent()
        agent.intelligence = mock_instance
        
        result = agent.execute({
            'product_description': 'Test product',
            'domain': 'Plant-Based',
            'max_competitors': 5
        })
        
        assert result['status'] == 'success'
        assert 'data' in result
        assert result['data']['count'] == 2

    def test_execute_missing_product(self):
        """Test execution with missing product description."""
        agent = CompetitorAgent()
        result = agent.execute({})
        
        assert result['status'] == 'error'
        assert 'product_description' in result['error']


class TestResearchAgent:
    """Tests for ResearchAgent."""

    def test_initialization(self):
        """Test research agent initialization."""
        agent = ResearchAgent(data_dir="test_data")
        assert agent.name == "ResearchAgent"
        assert agent.index_initialized == False

    def test_execute_not_initialized(self):
        """Test execution when not initialized."""
        agent = ResearchAgent(data_dir="test_data")
        result = agent.execute({
            'query': 'Test query'
        })
        
        assert result['status'] == 'error'
        assert 'not initialized' in result['error']

    def test_execute_missing_query(self):
        """Test execution with missing query."""
        agent = ResearchAgent(data_dir="test_data")
        agent.index_initialized = True
        result = agent.execute({})
        
        assert result['status'] == 'error'
        assert 'No query' in result['error']

    @patch('agents.research_agent.RAGEngine')
    def test_execute_success(self, mock_rag):
        """Test successful research query."""
        # Mock RAG engine
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.response = "Test answer"
        mock_response.source_nodes = [Mock(), Mock()]
        mock_instance.query.return_value = mock_response
        mock_instance.get_citations.return_value = [
            {'source': 'Paper 1', 'text': 'Citation 1'}
        ]
        
        agent = ResearchAgent(data_dir="test_data")
        agent.rag_engine = mock_instance
        agent.index_initialized = True
        
        result = agent.execute({
            'query': 'Test query',
            'domain': 'Plant-Based'
        })
        
        assert result['status'] == 'success'
        assert 'data' in result
        assert result['data']['query'] == 'Test query'


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator."""

    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = AgentOrchestrator(data_dir="test_data")
        assert orchestrator.research_agent is not None
        assert orchestrator.competitor_agent is not None
        assert orchestrator.marketing_agent is not None
        assert len(orchestrator.workflow_history) == 0

    def test_get_agent_status(self):
        """Test agent status retrieval."""
        orchestrator = AgentOrchestrator(data_dir="test_data")
        status = orchestrator.get_agent_status()
        
        assert 'research' in status
        assert 'competitor' in status
        assert 'marketing' in status
        assert 'research_initialized' in status

    def test_clear_history(self):
        """Test history clearing."""
        orchestrator = AgentOrchestrator(data_dir="test_data")
        orchestrator.workflow_history.append({'test': 'data'})
        
        orchestrator.clear_history()
        assert len(orchestrator.workflow_history) == 0

    @patch('agents.orchestrator.CompetitorAgent')
    @patch('agents.orchestrator.MarketingAgent')
    def test_execute_full_analysis(self, mock_marketing, mock_competitor):
        """Test full analysis execution."""
        # Mock competitor agent
        mock_comp_instance = Mock()
        mock_comp_instance.execute.return_value = {
            'status': 'success',
            'data': {
                'count': 5,
                'competitors': [],
                'statistics': {}
            }
        }
        mock_competitor.return_value = mock_comp_instance
        
        # Mock marketing agent
        mock_mark_instance = Mock()
        mock_mark_instance.execute.return_value = {
            'status': 'success',
            'data': {
                'segment': 'High Essentialist',
                'positioning': {},
                'messaging': {}
            }
        }
        mock_marketing.return_value = mock_mark_instance
        
        orchestrator = AgentOrchestrator(data_dir="test_data")
        orchestrator.competitor_agent = mock_comp_instance
        orchestrator.marketing_agent = mock_mark_instance
        
        result = orchestrator.execute_full_analysis(
            product_description="Test product",
            domain="Plant-Based",
            segment="High Essentialist"
        )
        
        assert result['status'] in ['success', 'partial']
        assert 'workflow' in result


class TestAgentConfig:
    """Tests for agent configuration."""

    def test_agent_config_defaults(self):
        """Test default configuration."""
        config = AgentConfig()
        assert config.data_dir == "data"
        assert config.persist_dir == ".storage"
        assert config.llm_provider == "openai"
        assert config.max_competitors == 10

    def test_get_workflow_template(self):
        """Test workflow template retrieval."""
        template = get_workflow_template(WorkflowType.FULL_ANALYSIS)
        assert template['name'] == "Full Market Intelligence Analysis"
        assert 'competitor' in template['agents']
        assert 'product_description' in template['required_params']

    def test_validate_task_params_success(self):
        """Test successful task validation."""
        task = {'product_description': 'Test', 'domain': 'Plant-Based'}
        is_valid, error = validate_task_params(task, ['product_description'])
        assert is_valid == True
        assert error == ""

    def test_validate_task_params_failure(self):
        """Test failed task validation."""
        task = {'domain': 'Plant-Based'}
        is_valid, error = validate_task_params(task, ['product_description'])
        assert is_valid == False
        assert 'product_description' in error

    def test_get_agent_capabilities(self):
        """Test agent capabilities retrieval."""
        capabilities = get_agent_capabilities()
        assert 'research' in capabilities
        assert 'competitor' in capabilities
        assert 'marketing' in capabilities
        assert 'orchestrator' in capabilities
        
        assert capabilities['research']['requires_initialization'] == True
        assert capabilities['competitor']['requires_initialization'] == False


class TestIntegration:
    """Integration tests for agent system."""

    def test_marketing_agent_all_segments(self):
        """Test marketing agent with all segments."""
        agent = MarketingAgent()
        
        for segment in ['High Essentialist', 'Skeptic', 'Non-Consumer']:
            result = agent.execute({
                'product_description': 'Test product',
                'segment': segment,
                'domain': 'Plant-Based'
            })
            
            assert result['status'] == 'success'
            assert result['data']['segment'] == segment

    def test_agent_history_tracking(self):
        """Test that agents track their history."""
        agent = MarketingAgent()
        
        # Execute multiple tasks
        for i in range(3):
            agent.execute({
                'product_description': f'Product {i}',
                'segment': 'High Essentialist'
            })
        
        history = agent.get_history()
        assert len(history) == 3
        
        status = agent.get_status()
        assert status['actions_count'] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
