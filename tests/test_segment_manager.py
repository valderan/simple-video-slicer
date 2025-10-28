from video_slicer.core.segment_manager import SegmentManager
from video_slicer.models.segment import Segment


def test_add_remove_segment():
    manager = SegmentManager()
    segment = Segment(start=0, end=10)
    manager.add_segment(segment)
    assert len(manager.segments) == 1
    assert manager.segments[0].index == 1

    manager.remove_segment(0)
    assert len(manager.segments) == 0


def test_reindex_after_removal():
    manager = SegmentManager()
    for idx in range(3):
        manager.add_segment(Segment(start=idx * 10, end=idx * 10 + 5))
    manager.remove_segment(1)
    assert [segment.index for segment in manager.segments] == [1, 2]
