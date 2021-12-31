import unittest

from mabooia import arg, get_args_obj


class ArgsTest(unittest.TestCase):

    test_args_01 = ["app", "--arg1", "--arg2", "value2", "--arg3", "value3"]
    test_args_02 = ["app", "--other", "other_value", "--arg3", "value3"]
    test_args_03 = ["app", "--arg1", "--arg2", "value2"]

    def test_passed_flag(self):
        args = get_args_obj(self._create_arg_def(), self.test_args_01)
        self.assertTrue(args.arg1)

    def test_not_passed_flag(self):
        args = get_args_obj(self._create_arg_def(), self.test_args_02)
        self.assertFalse(args.arg1)

    def test_passed_value(self):
        args = get_args_obj(self._create_arg_def(), self.test_args_01)
        self.assertEqual(args.arg2, "value2")

    def test_not_passed_value(self):
        args = get_args_obj(self._create_arg_def(), self.test_args_02)
        self.assertIsNone(args.arg2)

    def test_passed_required_arg(self):
        args = get_args_obj(self._create_arg_def(), self.test_args_01)
        self.assertEqual(args.arg3, "value3")

    def test_not_passed_required_arg(self):
        def call_func():
            get_args_obj(self._create_arg_def(), self.test_args_03)

        self.assertRaises(ValueError, call_func)

    @staticmethod
    def _create_arg_def():
        class Args:
            @arg(["--arg1"])
            def arg1(self) -> bool:
                pass

            @arg(["--arg2"])
            def arg2(self):
                pass

            @arg(["--arg3"], required=True)
            def arg3(self):
                pass

        return Args


if __name__ == '__main__':
    unittest.main()
