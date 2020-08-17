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

        distance = motion.calc_distance(time = 25, velocity = 100)
        velocity = motion.calc_velocity(time = 25, distance = distance)
        self.assertNear(distance, 1605, 0.01)
        self.assertNear(velocity, 100, 0.01)

    def test_params(self):
        motion = Motion(v_init = 10, v_final = 30, 
                accel = 10, decel = 5)
        f1, f2, a1, a2, t1, t2 = motion.calc_params(velocity = 5)
        self.assertEqual(f1, 1)
        self.assertEqual(f2, 1)
        self.assertEqual(a1, 5)
        self.assertEqual(a2, 10)
        f1, f2, a1, a2, t1, t2 = motion.calc_params(velocity = 10)
        self.assertEqual(f1, 0)
        self.assertEqual(f2, 1)
        self.assertEqual(a1, 0)
        self.assertEqual(a2, 10)
        f1, f2, a1, a2, t1, t2 = motion.calc_params(velocity = 20)
        self.assertEqual(f1, -1)
        self.assertEqual(f2, 1)
        self.assertEqual(a1, 10)
        self.assertEqual(a2, 10)
        f1, f2, a1, a2, t1, t2 = motion.calc_params(velocity = 30)
        self.assertEqual(f1, -1)
        self.assertEqual(f2, 0)
        self.assertEqual(a1, 10)
        self.assertEqual(a2, 0)
        f1, f2, a1, a2, t1, t2 = motion.calc_params(velocity = 40)
        self.assertEqual(f1, -1)
        self.assertEqual(f2, -1)
        self.assertEqual(a1, 10)
        self.assertEqual(a2, 5)

    def test_motion(self):
        motion = Motion(v_init = 10, v_final = 30, 
                accel = 10, decel = 5)

        distance = motion.calc_distance(velocity = 40, time = 10)
        time = motion.calc_time(velocity = 40, distance = distance)
        self.assertNear(time, 10)
        # time is equal than accel + decel time
        distance = motion.calc_distance(velocity = 40, time = 5)
        time = motion.calc_time(velocity = 40, distance = distance)
        self.assertNear(time, 5)
        # time is lower than accel and decel time
        distance = motion.calc_distance(velocity = 40, time = 3)
        self.assertNear(distance, 0)
        time = motion.calc_time(velocity = 40, distance = 100)
        self.assertNear(time, 3.82)
        velocity = motion.calc_velocity(distance = 100, time = time)
        self.assertNear(velocity, 36.06)
        distance = motion.calc_distance(velocity = velocity, time = time)
        self.assertNear(distance, 100)

    def test_velocity(self):
'''
    def test_motion_fastest_time(self):
        motion = Motion(v_init = 10, v_final = 30, 
                accel = 10, decel = 5)

        time = motion.calc_fastest_time(1611)
        self.assertNear(time, 25)
        '''

    
if __name__ == "__main__":
    unittest.main(exit=True)