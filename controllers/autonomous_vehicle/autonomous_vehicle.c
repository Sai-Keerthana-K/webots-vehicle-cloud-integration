/*
 * ORIGINAL WEBOTS AUTONOMOUS VEHICLE
 * + HYBRID MANUAL OVERRIDE (R2025a)
 */

#include <webots/camera.h>
#include <webots/device.h>
#include <webots/gps.h>
#include <webots/keyboard.h>
#include <webots/lidar.h>
#include <webots/robot.h>
#include <webots/vehicle/driver.h>

#include <math.h>
#include <stdio.h>
#include <string.h>

#define TIME_STEP 50
#define UNKNOWN 99999.9

// ---------------- PID (ORIGINAL DEMO VALUES) ----------------
#define KP 0.25
#define KI 0.006
#define KD 2.0

// ---------------- MANUAL OVERRIDE ----------------
#define MANUAL_SPEED_STEP 2.0
#define MANUAL_STEER_STEP 0.02
#define OVERRIDE_DECAY 0.90

// ---------------- DEVICES ----------------
WbDeviceTag camera;
WbDeviceTag lidar;

// ---------------- STATE ----------------
double speed = 0.0;
double steering_angle = 0.0;

// manual override offsets
double manual_speed_offset = 0.0;
double manual_steer_offset = 0.0;

// camera
int camera_width;
int camera_height;
double camera_fov;

// lidar
int lidar_width;

// PID
double pid_integral = 0.0;
double pid_prev = 0.0;

// ---------------- UTILS ----------------
double clamp(double v, double min, double max) {
  if (v < min) return min;
  if (v > max) return max;
  return v;
}

int color_diff(const unsigned char a[3], const unsigned char b[3]) {
  int diff = 0;
  for (int i = 0; i < 3; i++)
    diff += abs(a[i] - b[i]);
  return diff;
}

// ---------------- CAMERA PROCESSING (ORIGINAL) ----------------
double process_camera_image(const unsigned char *image) {
  const unsigned char REF[3] = {95, 187, 203}; // yellow
  int sumx = 0, count = 0;

  for (int y = camera_height / 2; y < camera_height; y++) {
    for (int x = 0; x < camera_width; x++) {
      const unsigned char *p = image + 4 * (y * camera_width + x);
      if (color_diff(p, REF) < 30) {
        sumx += x;
        count++;
      }
    }
  }

  if (count == 0)
    return UNKNOWN;

  double avg = (double)sumx / count;
  return (avg / camera_width - 0.5) * camera_fov;
}

// ---------------- PID ----------------
double apply_pid(double error) {
  pid_integral += error;
  double diff = error - pid_prev;
  pid_prev = error;
  return KP * error + KI * pid_integral + KD * diff;
}

// ---------------- LIDAR OBSTACLE ----------------
double obstacle_steering(const float *ranges) {
  int center = lidar_width / 2;
  int span = lidar_width / 10;
  double steer = 0.0;
  int hits = 0;

  for (int i = center - span; i < center + span; i++) {
    if (ranges[i] > 0.1 && ranges[i] < 7.0) {
      steer += (center - i) * 0.002;
      hits++;
    }
  }

  if (hits > 0)
    return steer;

  return 0.0;
}

// ---------------- MAIN ----------------
int main() {
  wbu_driver_init();
  wb_keyboard_enable(TIME_STEP);

  camera = wb_robot_get_device("camera");
  lidar = wb_robot_get_device("Sick LMS 291");

  wb_camera_enable(camera, TIME_STEP);
  wb_lidar_enable(lidar, TIME_STEP);

  camera_width = wb_camera_get_width(camera);
  camera_height = wb_camera_get_height(camera);
  camera_fov = wb_camera_get_fov(camera);

  lidar_width = wb_lidar_get_horizontal_resolution(lidar);

  printf("AUTO MODE ACTIVE (Hybrid Override Enabled)\n");

  // original demo cruise speed
  wbu_driver_set_cruising_speed(50.0);

  while (wbu_driver_step() != -1) {

    // ---------------- AUTONOMY ----------------
    const unsigned char *img = wb_camera_get_image(camera);
    const float *ranges = wb_lidar_get_range_image(lidar);

    double auto_steer = 0.0;
    double auto_speed = 50.0;

    double angle = process_camera_image(img);
    if (angle != UNKNOWN)
      auto_steer = apply_pid(angle);

    auto_steer += obstacle_steering(ranges);

    // ---------------- MANUAL OVERRIDE ----------------
    int key = wb_keyboard_get_key();

    if (key == WB_KEYBOARD_UP)
      manual_speed_offset += MANUAL_SPEED_STEP;
    if (key == WB_KEYBOARD_DOWN)
      manual_speed_offset -= MANUAL_SPEED_STEP;
    if (key == WB_KEYBOARD_LEFT)
      manual_steer_offset -= MANUAL_STEER_STEP;
    if (key == WB_KEYBOARD_RIGHT)
      manual_steer_offset += MANUAL_STEER_STEP;

    if (key == -1) {
      manual_speed_offset *= OVERRIDE_DECAY;
      manual_steer_offset *= OVERRIDE_DECAY;
    }

    // ---------------- APPLY ----------------
    wbu_driver_set_cruising_speed(
      clamp(auto_speed + manual_speed_offset, 0.0, 70.0)
    );

    wbu_driver_set_steering_angle(
      clamp(auto_steer + manual_steer_offset, -0.5, 0.5)
    );
  }

  wbu_driver_cleanup();
  return 0;
}
