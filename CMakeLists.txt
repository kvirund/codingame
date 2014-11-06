cmake_minimum_required(VERSION 2.8)

project(codingame)

add_subdirectory(easy/onboarding)
add_subdirectory(easy/skynet.the.chasm)
add_subdirectory(easy/the.descent)
add_subdirectory(easy/power.of.thor)
add_subdirectory(easy/mars.lander)
add_subdirectory(easy/temperatures)
add_subdirectory(easy/ascii.art)
add_subdirectory(easy/chuck.norris)
add_subdirectory(easy/mime.type)
add_subdirectory(easy/defibrillators)
add_subdirectory(easy/horse.racing.duals)

add_subdirectory(medium/skynet.the.virus)
add_subdirectory(medium/heat.detector)

add_definitions(-Wall -g -00)
