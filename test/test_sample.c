#include "unity.h"

// A sample test case
void test_addition(void) {
    TEST_ASSERT_EQUAL_INT(32, (30 + 2));
}

// Another sample test case
void test_subtraction(void) {
    TEST_ASSERT_EQUAL_INT(10, (20 - 10));
}

// The test runner function that will be called from main
void run_test_suite(void) {
    RUN_TEST(test_addition);
    RUN_TEST(test_subtraction);
}
