# Ride-sharing-Simulator
A high-capacity ride-sharing simulator calibrated by real request datasets and road networks

<div align="center">
    <img src="intro-images/Simulator_Architecture.jpg", width="700" alt><br>
    Simulator Architecture
</div>
\begin{array}{|l|c|c|c|c|c|}
\hline
\text{Method} & \text{Service Rate} & \text{assigning} & \text{pick-up} & \text{detour} & \text{vehicles} \\
& & \text{AVG time(min)} & \text{AVG time(min)} & \text{AVG time(min)} & \text{total income(USD)} \\
\hline
\text{Reinforcement Learning} & 0.4291 & \textcolor{blue}{2.29} & \textcolor{red}{3.27} & \textcolor{blue}{1.54} & \textcolor{blue}{28779.54} \\
\text{Pre} & 0.41 & 2.95 & 2.99 & {5.08} & \textcolor{red}{25352.95} \\
\text{Pre+Cot} & 0.44 & \textcolor{red}{3.17} & 2.62 & 4.76 & 26959.48 \\
\text{Pre+Cot+income} & \textcolor{red}{0.373} & 3.08 & 2.81 & \textcolor{red}{5.54} & 27457.53 \\
\text{Pre+Cot+service-rate} & 0.465 & 3.10 & 2.80 & 4.37 & 27004.67 \\
\text{Pre+Cot+society} & \textcolor{blue}{0.469} & 3.12 & \textcolor{blue}{2.54} & 4.44 & 27445.41 \\
\hline
\end{array}
## Updating...
- [x] Implement dispatching and repositioning algorithms of ride-sharing and ride-sourcing
- [x] Add traffic flow models to measure traffic congestion, speed, and carbon emissions
- [x] Implement 2D visualization
- [ ] Provide implementation for Reinforcement Learning algorithms
- [ ] Provide implementation for car-following models
- [ ] Provide implementation for highly realistic 3D visualization


## Setup
1. Install dependencies and libraries
``` bash
pip install -r requirements.txt
```
2. Download [Road Network](https://drive.google.com/file/d/1plVhAfyD0ZtiFEfIHL8HYrPuLczdtvH0/view?usp=share_link) into **data** filefold

## Simulation
### Run the demo
```bash
python simulation.py --cfg ./config/test.yaml  --DrawResult True
```

### Simulation results
[![Demonstration for simulation results](https://res.cloudinary.com/marcomontalbano/image/upload/v1683018353/video_to_markdown/images/youtube--upBATpfreoI-c05b58ac6eb4c4700831b2b3070cd403.jpg)](https://youtu.be/upBATpfreoI "Demonstration for simulation results")



## Dispatching Algorithm
<div align="center">
    <img src="intro-images/DispatchingAlgorithm.jpg", width="700" alt><br>
</div>

**Dispatching Algorithm.** (a) Passengers are preassigned to vehicles within their matching areas; then (b) each vehicle will be potentially scheduled with multiple passengers. (c) The platform checks the shareability of each vehicle's potential passengers by planning the shortest routes and verifying pickup and detour time constraints, e.g., Passengers 1 and 2 can share Vehicle 1, but Passengers 2 and 3 cannot share Vehicle 2 due to the detour time constraint. (d) RTV-graph can be established to connect all potential trips (including one or more requests) to vehicles. (e) The optimal matching results are obtained via ILP. (f) Vehicles pick up and deliver passengers according to the matching results of (e) and the planned shortest routes of (c).
