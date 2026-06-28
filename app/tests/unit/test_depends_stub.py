import pytest
from unittest.mock import Mock
from app.presentation.depends_stub import Stub


class TestStub:
    """Unit tests for Stub class"""
    
    def test_stub_initialization_with_dependency_only(self):
        """Test Stub initialization with only dependency"""
        mock_dependency = Mock()
        stub = Stub(mock_dependency)
        
        assert stub._dependency == mock_dependency
        assert stub._kwargs == {}
    
    def test_stub_initialization_with_kwargs(self):
        """Test Stub initialization with dependency and kwargs"""
        mock_dependency = Mock()
        kwargs = {"param1": "value1", "param2": "value2"}
        stub = Stub(mock_dependency, **kwargs)
        
        assert stub._dependency == mock_dependency
        assert stub._kwargs == kwargs
    
    def test_stub_call_raises_not_implemented_error(self):
        """Test that calling a Stub raises NotImplementedError"""
        mock_dependency = Mock()
        stub = Stub(mock_dependency)
        
        with pytest.raises(NotImplementedError):
            stub()
    
    def test_stub_equality_same_dependency_no_kwargs(self):
        """Test Stub equality with same dependency and no kwargs"""
        mock_dependency = Mock()
        stub1 = Stub(mock_dependency)
        stub2 = Stub(mock_dependency)
        
        assert stub1 == stub2
        assert stub1 == mock_dependency
    
    def test_stub_equality_different_dependency(self):
        """Test Stub equality with different dependencies"""
        mock_dependency1 = Mock()
        mock_dependency2 = Mock()
        stub1 = Stub(mock_dependency1)
        stub2 = Stub(mock_dependency2)
        
        assert stub1 != stub2
        assert stub1 != mock_dependency2
    
    def test_stub_equality_with_kwargs(self):
        """Test Stub equality with kwargs"""
        mock_dependency = Mock()
        stub1 = Stub(mock_dependency, param1="value1")
        stub2 = Stub(mock_dependency, param1="value1")
        stub3 = Stub(mock_dependency, param1="value2")
        
        assert stub1 == stub2
        assert stub1 != stub3
        assert stub1 != mock_dependency  # Should not equal dependency when kwargs present
    
    def test_stub_equality_with_different_kwargs(self):
        """Test Stub equality with different kwargs"""
        mock_dependency = Mock()
        stub1 = Stub(mock_dependency, param1="value1")
        stub2 = Stub(mock_dependency, param2="value2")
        
        assert stub1 != stub2
    
    def test_stub_equality_with_other_types(self):
        """Test Stub equality with non-Stub objects"""
        mock_dependency = Mock()
        stub = Stub(mock_dependency)
        
        assert stub != "string"
        assert stub != 123
        assert stub != Mock()
    
    def test_stub_hash_no_kwargs(self):
        """Test Stub hash with no kwargs"""
        mock_dependency = Mock()
        stub = Stub(mock_dependency)
        
        expected_hash = hash(mock_dependency)
        assert hash(stub) == expected_hash
    
    def test_stub_hash_with_kwargs(self):
        """Test Stub hash with kwargs"""
        mock_dependency = Mock()
        stub = Stub(mock_dependency, param1="value1", param2="value2")
        
        expected_hash = hash((mock_dependency, ("param1", "value1"), ("param2", "value2")))
        assert hash(stub) == expected_hash
    
    def test_stub_hash_consistency(self):
        """Test that Stub hash is consistent for same inputs"""
        mock_dependency = Mock()
        stub1 = Stub(mock_dependency, param1="value1")
        stub2 = Stub(mock_dependency, param1="value1")
        
        assert hash(stub1) == hash(stub2)
    
    def test_stub_hash_different_kwargs_order(self):
        """Test that Stub hash is consistent regardless of kwargs order"""
        mock_dependency = Mock()
        stub1 = Stub(mock_dependency, param1="value1", param2="value2")
        stub2 = Stub(mock_dependency, param2="value2", param1="value1")
        
        # Note: This test might fail if the hash implementation doesn't handle
        # kwargs order consistently. The current implementation uses items()
        # which should maintain consistent ordering in Python 3.7+
        assert hash(stub1) == hash(stub2) 