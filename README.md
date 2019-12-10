# AppDrone4IoT: Flights Scheduling Service and Trajectory Optimization of UAV as Data Mule

This project aims to provide a uav flight plan through a trajectory optimization algorithm, to generate a mavlink file, integrating with ROS driver in order to simulate a flight in sphinx.

## Getting Started

TODO - links to download bebop_autonomy (Driver ROS) and parrot sphinx.

### Prerequisites

TODO - What things you need to install the software and how to install them.

### Installing

TODO - A step by step series of examples that tell you how to get a development env running

TODO - Say what the step will be

## Running simulations

### Starting firmware 

Once you got all steps of the installation you need start the firmware service.

Before start the firmware service make sure there isn't a instance already running by looking for it.

```
ps ax|grep firmwared
```

If you find any other:

```
sudo systemctl stop firmwared.service
```

So to start the firmware:

```
sudo systemctl start firmwared.service
```

Verify if it's running:

```
fdc ping
```

End with an example of getting some data out of the system or using it for a little demo

### Executing the simulator

If you're running a simulation for Bebop 2, open the configuration file:

```
nano opt/parrot-sphinx/usr/share/sphinx/drones/bebop2.drone

```
I rather to keep the file the same way the installation create. Make sure it looks like this:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<drone
  name="bebop2"
  firmware="http://plf.parrot.com/sphinx/firmwares/ardrone3/milos_pc/latest/images/ardrone3-milos_pc.ext2.zip"
  hardware="milosboard">
  <machine_params
    low_gpu="0"
    with_front_cam="1"
    with_hd_battery="0"
    with_flir="0"
    flir_pos="tilted"/>
  <pose>default</pose>
  <interface>eth1</interface>
  <!-- 'wlan0' may need to be replaced the actual wifi interface name -->
  <stolen_interface>wlan0:eth0:192.168.42.1/24</stolen_interface>
</drone>

```

Some parameters are changed by executing the simulator. So you can set false to the use of frontal camera,
and pass the Wi-Fi interface name.

For execute the simulator:
```
sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/bebop2.drone::with_front_cam=false::stolen_interface=wlp4s0:wlp4s0:192.168.42.1/24

```

If you wanna see it with a scenario:

```
sphinx /opt/parrot-sphinx/usr/share/sphinx/worlds/outdoor_5.world 
 /opt/parrot-sphinx/usr/share/sphinx/drones/bebop2.drone::with_front_cam=false::stolen_interface=wlp4s0:wlp4s0:192.168.42.1/24

```


### And coding style tests

Explain what these tests test and why



## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

