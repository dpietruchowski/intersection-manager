import unittest
from intersection.motion import Motion
import pdb


class TestMotion(unittest.TestCase):
    def assertNear(self, value, expected, diff=0.05):
        self.assertTrue(abs(value - expected) < diff, 
                'value: %f, expected: %f, diff: %f' % (value, expected, abs(value - expected)))
        
    def test_motion_points(self):
        motion = Motion(v_init = 10, v_final = 30, 
                accel = 10, decel = 5)
        d, t = motion.calc_accel_distance_time(velocity = 100)
        self.assertEqual(d, 495)
        self.assertEqual(t, 9)
        d, t = motion.calc_decel_distance_time(velocity = 100)
        self.assertEqual(d, 910)
        self.assertEqual(t, 14)
        motion_points = motion.calc_motion_points(velocity = 100, time = 25)
        self.assertEqual(motion_points[0].d, 0)
        self.assertEqual(motion_points[0].t, 0)
        self.assertEqual(motion_points[0].v, 10)
        self.assertEqual(motion_points[1].d, 495)
        self.assertEqual(motion_points[1].t, 9)
        self.assertEqual(motion_points[1].v, 100)
        self.assertEqual(motion_points[2].d, 695)
        self.assertEqual(motion_points[2].t, 11)
        self.assertEqual(motion_points[2].v, 100)
        self.assertEqual(motion_points[3].d, 1605)
        self.assertEqual(motion_points[3].t, 25)
        self.assertEqual(motion_points[3].v, 30)


    def test_motion_velocity(self):
        motion = Motion(v_init = 10, v_final = 30, 
                accel = 10, decel = 5)

        velocity = motion.calc_velocity(time = 25, distance = 1605)
        self.assertNear(velocity, 100)

        velocity = motion.calc_velocity(time = 300, distance = 1605)
        self.assertNear(velocity, 5.24)

    
    def test_motion_max_distance(self):
        motion = Motion(v_init = 10, v_final = 30, 
                accel = 10, decel = 5)

        distance = motion.calc_max_distance(time = 25, v_max = 100)
        velocity = motion.calc_velocity(time = 25, distance = distance)
        self.assertNear(distance, 1605, 0.01)
        self.assertNear(velocity, 100, 0.01)
'''
    def test_motion_fastest_time(self):
        motion = Motion(v_init = 10, v_final = 30, 
                accel = 10, decel = 5)

        time = motion.calc_fastest_time(1611)
        self.assertNear(time, 25)
        '''

    
if __name__ == "__main__":
    unittest.main(exit=True)