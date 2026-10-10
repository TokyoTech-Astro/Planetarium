import unittest
from pathlib import Path
from app import load_timeline, timeline_motor_position

class TimelinePositionTest(unittest.TestCase):
    def test_legacy_show_positions(self):
        rows=load_timeline(Path(__file__).parent.parent/'操作者用'/'2024番組_指示送信設定.txt')
        next(row for row in rows if row['time']==316)['angle']=240
        rows[-2]['speed']=-3
        self.assertAlmostEqual(timeline_motor_position(rows,157),30,places=4)
        self.assertAlmostEqual(timeline_motor_position(rows,207),30+50*.189873,places=4)
        self.assertAlmostEqual(timeline_motor_position(rows,316),60,places=3)
        self.assertAlmostEqual(timeline_motor_position(rows,380),240,places=3)
        self.assertAlmostEqual(timeline_motor_position(rows,834),0,places=3)
    def test_signed_direction_and_equal_target(self):
        rows=[dict(time=0,angle=90,speed=5),dict(time=18,angle=0,speed=-5)]
        self.assertEqual(timeline_motor_position(rows,27),45)
        self.assertEqual(timeline_motor_position(rows,36),0)
        self.assertEqual(timeline_motor_position([dict(time=0,angle=0,speed=5)],100),0)
    def test_corrected_gemini_target(self):
        rows=load_timeline(Path(__file__).parent.parent/'操作者用'/'2024番組_指示送信設定.txt')
        self.assertAlmostEqual(timeline_motor_position(rows,380),200,places=3)

if __name__=='__main__':unittest.main()
