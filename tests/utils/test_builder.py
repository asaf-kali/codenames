import random

import pytest

from codenames.utils.builder import ExtractResult, extract_random_subset


def test_extract_random_subset_returns_correct_types():
    """Test that extract_random_subset returns ExtractResult with tuples."""
    elements = ["a", "b", "c", "d", "e"]
    result = extract_random_subset(elements, 2)

    assert isinstance(result, ExtractResult)
    assert isinstance(result.remaining, tuple)
    assert isinstance(result.sample, tuple)


def test_extract_random_subset_correct_sizes():
    """Test that extract_random_subset returns correct sizes."""
    elements = ["a", "b", "c", "d", "e"]
    result = extract_random_subset(elements, 2)

    assert len(result.sample) == 2
    assert len(result.remaining) == 3
    assert len(result.sample) + len(result.remaining) == len(elements)


def test_extract_random_subset_no_overlap():
    """Test that sample and remaining don't overlap."""
    elements = ["a", "b", "c", "d", "e"]
    result = extract_random_subset(elements, 2)

    assert set(result.sample).isdisjoint(set(result.remaining))


def test_extract_random_subset_all_elements_present():
    """Test that all original elements are in sample or remaining."""
    elements = ["a", "b", "c", "d", "e"]
    result = extract_random_subset(elements, 2)

    all_result_elements = set(result.sample) | set(result.remaining)
    assert all_result_elements == set(elements)


def test_extract_random_subset_zero_size():
    """Test extracting zero elements."""
    elements = ["a", "b", "c"]
    result = extract_random_subset(elements, 0)

    assert len(result.sample) == 0
    assert len(result.remaining) == 3
    assert set(result.remaining) == set(elements)


def test_extract_random_subset_all_elements():
    """Test extracting all elements."""
    elements = ["a", "b", "c"]
    result = extract_random_subset(elements, 3)

    assert len(result.sample) == 3
    assert len(result.remaining) == 0
    assert set(result.sample) == set(elements)


def test_extract_random_subset_single_element():
    """Test extracting from single element collection."""
    elements = ["a"]
    result = extract_random_subset(elements, 1)

    assert result.sample == ("a",)
    assert result.remaining == ()


def test_extract_random_subset_is_random():
    """Test that extract_random_subset produces different results."""
    elements = list(range(20))
    results = [extract_random_subset(elements, 10) for _ in range(5)]

    # At least some results should be different (very high probability)
    unique_samples = {result.sample for result in results}
    assert len(unique_samples) > 1


def test_extract_random_subset_with_seed_is_reproducible():
    """Test that using same seed produces same results."""
    elements = list(range(20))

    random.seed(42)
    result1 = extract_random_subset(elements, 10)

    random.seed(42)
    result2 = extract_random_subset(elements, 10)

    assert result1.sample == result2.sample
    assert result1.remaining == result2.remaining


def test_extract_random_subset_with_tuple_input():
    """Test extract_random_subset works with tuple input."""
    elements = ("a", "b", "c", "d")
    result = extract_random_subset(elements, 2)

    assert len(result.sample) == 2
    assert len(result.remaining) == 2


def test_extract_random_subset_with_set_input():
    """Test extract_random_subset works with set input."""
    elements = {"a", "b", "c", "d"}
    result = extract_random_subset(elements, 2)

    assert len(result.sample) == 2
    assert len(result.remaining) == 2
    assert set(result.sample) | set(result.remaining) == elements


def test_extract_random_subset_raises_on_too_large_sample():
    """Test that requesting more elements than available raises error."""
    elements = ["a", "b", "c"]
    with pytest.raises(ValueError):
        extract_random_subset(elements, 5)


def test_extract_random_subset_preserves_element_type():
    """Test that element types are preserved."""
    elements = [1, 2, 3, 4, 5]
    result = extract_random_subset(elements, 2)

    assert all(isinstance(x, int) for x in result.sample)
    assert all(isinstance(x, int) for x in result.remaining)


def test_extract_random_subset_with_duplicates_in_input():
    """Test behavior with duplicate elements in input."""
    elements = ["a", "a", "b", "b", "c"]
    result = extract_random_subset(elements, 2)

    # Should select 2 items from the collection
    assert len(result.sample) == 2
    # Remaining should have the others
    assert len(result.remaining) == 3


def test_extract_result_named_tuple_access():
    """Test that ExtractResult can be accessed by index and by name."""
    result = ExtractResult(remaining=("a", "b"), sample=("c", "d"))

    # Access by name
    assert result.remaining == ("a", "b")
    assert result.sample == ("c", "d")

    # Access by index
    assert result[0] == ("a", "b")
    assert result[1] == ("c", "d")


def test_extract_random_subset_empty_input():
    """Test extract_random_subset with empty collection."""
    elements = []
    result = extract_random_subset(elements, 0)

    assert result.sample == ()
    assert result.remaining == ()


def test_extract_random_subset_with_complex_objects():
    """Test extract_random_subset with complex objects."""
    elements = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
    result = extract_random_subset(elements, 2)

    assert len(result.sample) == 2
    assert len(result.remaining) == 2
    assert all(isinstance(obj, dict) for obj in result.sample)