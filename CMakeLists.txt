cmake_minimum_required(VERSION 3.15...3.27)
project(klaycircuits LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# -----------------------------------------------
# DEPENDENCIES 
# -----------------------------------------------

include(GNUInstallDirs)
if(SKBUILD)
  find_package(Python 3.10
          REQUIRED COMPONENTS Interpreter Development.Module
          OPTIONAL_COMPONENTS Development.SABIModule)

  find_package(nanobind CONFIG REQUIRED)
endif()
# -----------------------------------------------
# LIBRARY KLAY
# -----------------------------------------------

add_library(klay SHARED
  src/circuit.cpp
  src/node.cpp
)

set_target_properties(klay PROPERTIES
  WINDOWS_EXPORT_ALL_SYMBOLS ON
)

if(SKBUILD)
  set(KLAY_LIB_DEST     klay)
  set(KLAY_INCLUDE_DEST klay/include)
  set(KLAY_CMAKE_DEST   klay/cmake/klay)
else()
  set(KLAY_LIB_DEST     ${CMAKE_INSTALL_LIBDIR})
  set(KLAY_INCLUDE_DEST ${CMAKE_INSTALL_INCLUDEDIR})
  set(KLAY_CMAKE_DEST   ${CMAKE_INSTALL_LIBDIR}/cmake/klay)
endif()

target_include_directories(klay
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${KLAY_INCLUDE_DEST}>
)

install(TARGETS klay
  EXPORT klayTargets
  RUNTIME DESTINATION ${KLAY_LIB_DEST}
  LIBRARY DESTINATION ${KLAY_LIB_DEST}
)

install(DIRECTORY include/
  DESTINATION ${KLAY_INCLUDE_DEST}
)

install(EXPORT klayTargets
  FILE        klayConfig.cmake
  DESTINATION ${KLAY_CMAKE_DEST}
)

# -----------------------------------------------
# PYTHON KLAY EXTENSION
# -----------------------------------------------
if(SKBUILD)
  nanobind_add_module(klay_ext
    STABLE_ABI
    NOMINSIZE
    NB_STATIC
    src/klay_bindings.cpp
    src/indices.cpp
  )

  target_link_libraries(klay_ext PRIVATE klay)

  set(RPATH_ORIGIN "$ORIGIN")
  if(APPLE)
    set(RPATH_ORIGIN "@loader_path")
  endif()

  set_target_properties(klay_ext PROPERTIES
    INSTALL_RPATH "${RPATH_ORIGIN}"
    BUILD_WITH_INSTALL_RPATH TRUE
  )

  install(TARGETS klay_ext LIBRARY DESTINATION klay)
endif()
# -----------------------------------------------
# PYTHON KLAY EXTENSION STUBS
# -----------------------------------------------
# nanobind_add_stub(
#   klay_ext_stub
#   INSTALL_TIME
#   MODULE klay_ext
#   OUTPUT klay/klay_ext.pyi
#   PYTHON_PATH "klay"
#   MARKER_FILE klay/py.typed
#   DEPENDS klay_ext
# )
# install(FILES "${CMAKE_BINARY_DIR}/klay_ext.pyi" DESTINATION klay)
