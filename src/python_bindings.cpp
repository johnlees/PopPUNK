/*
 * sketchlib_bindings.cpp
 * Python bindings for PopPUNK C++ functions
 *
 */

// pybind11 headers
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

#include "boundary.hpp"

// Wrapper which makes a ref to the python/numpy array
Eigen::VectorXf assignThreshold(const Eigen::Ref<NumpyMatrix> &distMat,
                                const int slope,
                                const double x_max,
                                const double y_max,
                                const unsigned int num_threads = 1)
{
  Eigen::VectorXf assigned = assign_threshold(distMat,
                                              slope,
                                              x_max,
                                              y_max,
                                              num_threads);
  return (assigned);
}

network_coo thresholdIterate1D(const Eigen::Ref<NumpyMatrix> &distMat,
                 const std::vector<double> &offsets,
                 const int slope,
                 const double x0,
                 const double y0,
                 const double x1,
                 const double y1,
                 const int num_threads)
{
  if (!std::is_sorted(offsets.begin(), offsets.end()))
  {
    throw std::runtime_error("Offsets to thresholdIterate1D must be sorted");
  }
  std::tuple<std::vector<long>, std::vector<long>, std::vector<long>> add_idx =
      threshold_iterate_1D(distMat, offsets, slope, x0, y0, x1, y1, num_threads);
  return (add_idx);
}

network_coo thresholdIterate2D(const Eigen::Ref<NumpyMatrix> &distMat,
                 const std::vector<float> &x_max,
                 const float y_max)
{
  if (!std::is_sorted(x_max.begin(), x_max.end()))
  {
    throw std::runtime_error("x_max range to thresholdIterate2D must be sorted");
  }
  std::tuple<std::vector<long>, std::vector<long>, std::vector<long>> add_idx =
      threshold_iterate_2D(distMat, x_max, y_max);
  return (add_idx);
}

PYBIND11_MODULE(poppunk_refine, m)
{
  m.doc() = "Network refine helper functions";

  // Exported functions
  m.def("assignThreshold", &assignThreshold, py::return_value_policy::reference_internal, "Assign samples based on their relation to a 2D boundary",
        py::arg("distMat").noconvert(),
        py::arg("slope"),
        py::arg("x_max"),
        py::arg("y_max"),
        py::arg("num_threads") = 1);

  m.def("thresholdIterate1D", &thresholdIterate1D, py::return_value_policy::reference_internal, "Move a 2D boundary to grow a network by adding edges at each offset",
        py::arg("distMat").noconvert(),
        py::arg("offsets"),
        py::arg("slope"),
        py::arg("x0"),
        py::arg("y0"),
        py::arg("x1"),
        py::arg("y1"),
        py::arg("num_threads") = 1);

  m.def("thresholdIterate2D", &thresholdIterate2D, py::return_value_policy::reference_internal, "Move a 2D boundary to grow a network by adding edges at each offset",
        py::arg("distMat").noconvert(),
        py::arg("x_max"),
        py::arg("y_max"));
}
