# Literature Map

## Field Box

This paper sits in contact-rich manipulation and control: force/impedance/admittance control, hybrid contact dynamics, tactile manipulation, contact-mode estimation, time-delay control, and passivity/teleoperation. The narrow field box is not generic robot learning; it is the controller-level question of what a robot should do when the semantic timestamp of contact evidence is wrong during a physical interaction.

## Sweep Coverage

- Total rows in matrix: 1242
- landscape_sweep_metadata: 700
- overflow_not_counted_in_1000_target: 242
- deep_read_abstract_metadata: 225
- serious_skim_abstract_metadata: 75
- Important limitation: rows are extracted from OpenAlex metadata and abstracts. The paper text separately cites and reasons about the closest mechanisms.

## Query Buckets In The Counted 1000

- contact_rich_manipulation: 434
- contact_dynamics: 290
- force_control: 276

## Year Distribution Snapshot

- 2025: 1
- 2024: 15
- 2023: 51
- 2022: 49
- 2021: 87
- 2020: 103
- 2019: 90
- 2018: 94
- 2017: 70
- 2016: 56
- 2015: 45
- 2014: 45
- 2013: 44
- 2012: 36
- 2011: 24
- 2010: 19
- 2009: 17
- 2008: 16
- 2007: 13
- 2006: 16
- 2005: 10
- 2004: 16
- 2003: 14
- 2002: 6
- 2001: 8

## Mechanism Clusters

- introduce a controller, estimator, planner, or analysis for physical interaction: 717
- learn policy, model, or representation from demonstrations or trial data: 172
- trigger control or estimation updates on detected events: 70
- estimate contact properties from tactile images or taxel signals: 40
- shape apparent mass-damping-stiffness at the end-effector: 14
- split task space into force-controlled and position-controlled subspaces: 10
- enforce passivity or energy balance under communication delay: 6
- map measured force to commanded motion through virtual dynamics: 2
- solve receding-horizon constrained optimization with a contact model: 2
- predict current plant state from delayed measurements: 2
- encode unilateral contact and friction with complementarity constraints: 1

## Repeated Open Gaps

- semantic mismatch between delayed contact observations and current hybrid mode: 748
- explicit contact-latency state variables and latency-invariant contact-age control: 203
- out-of-distribution timing shifts with the same geometry and policy: 152
- how tactile latency changes the controller's inferred contact age: 40
- whether contact event timing mismatch should be estimated as its own state: 19
- task-level contact force transients, not only stability, under delayed contact sensing: 19
- how compliance should be phased by contact age rather than wall-clock time: 16

## Top 50 Deep-Read Candidates

| Rank | Year | Title | Mechanism | Leaves Open |
|---:|---:|---|---|---|
| 1 | 2020 | Learning Force Control for Contact-Rich Manipulation Tasks With Rigid Position-Controll... | map measured force to commanded motion through virtual dynamics; learn policy... | semantic mismatch between delayed contact observations and current hybrid mode | how co... |
| 2 | 2022 | A review on reinforcement learning for contact-rich robotic manipulation tasks | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 3 | 2020 | Variable Compliance Control for Robotic Peg-in-Hole Assembly: A Deep-Reinforcement-Lear... | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 4 | 2018 | Tactile Sensors for Friction Estimation and Incipient Slip Detection—Toward Dexterous R... | estimate contact properties from tactile images or taxel signals; trigger con... | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 5 | 2022 | A survey of robot manipulation in contact | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 6 | 2015 | Learning contact-rich manipulation skills with guided policy search | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 7 | 1993 | Coordinated Dynamic Hybrid Position/Force Control for Multiple Robot Manipulators Handl... | split task space into force-controlled and position-controlled subspaces | semantic mismatch between delayed contact observations and current hybrid mode |
| 8 | 2023 | Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 9 | 2019 | Dexterous Manipulation with Deep Reinforcement Learning: Efficient, General, and Low-Cost | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 10 | 1997 | AMADEUS: advanced manipulation for deep underwater sampling | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode |
| 11 | 2003 | Object impedance control for cooperative manipulation: theory and experimental results | shape apparent mass-damping-stiffness at the end-effector | semantic mismatch between delayed contact observations and current hybrid mode | how co... |
| 12 | 1992 | Object impedance control for cooperative manipulation: theory and experimental results | shape apparent mass-damping-stiffness at the end-effector | semantic mismatch between delayed contact observations and current hybrid mode | how co... |
| 13 | 2015 | Toward a New Generation of Electrically Controllable Hygromorphic Soft Actuators | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 14 | 2019 | Soft Magnetic Skin for Continuous Deformation Sensing | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 15 | 1989 | Grasping and Coordinated Manipulation by a Multifingered Robot Hand | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 16 | 2013 | A direct method for trajectory optimization of rigid bodies through contact | encode unilateral contact and friction with complementarity constraints | semantic mismatch between delayed contact observations and current hybrid mode |
| 17 | 2021 | Recovery RL: Safe Reinforcement Learning With Learned Recovery Zones | learn policy, model, or representation from demonstrations or trial data; tri... | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 18 | 2017 | A Mathematical Introduction to Robotic Manipulation | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 19 | 2020 | Triboelectric nanogenerator sensors for soft robotics aiming at digital twin applications | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 20 | 1999 | A Steady-Hand Robotic System for Microsurgical Augmentation | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 21 | 2011 | Bilateral Telemanipulation With Time Delays: A Two-Layer Approach Combining Passivity a... | enforce passivity or energy balance under communication delay | whether contact event timing mismatch should be estimated as its own state | task-level... |
| 22 | 2011 | The role of feed-forward and feedback processes for closed-loop prosthesis control | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 23 | 1990 | Foundations of Robotics | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 24 | 2014 | Flexible Three‐Axial Force Sensor for Soft and Highly Sensitive Artificial Touch | estimate contact properties from tactile images or taxel signals; trigger con... | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 25 | 1988 | On the stability of manipulators performing contact tasks | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 26 | 2017 | WALK‐MAN: A High‐Performance Humanoid Platform for Realistic Environments | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 27 | 2005 | Sampled data systems passivity and discrete port-Hamiltonian systems | enforce passivity or energy balance under communication delay | whether contact event timing mismatch should be estimated as its own state | task-level... |
| 28 | 2019 | Electronic Skin: Recent Progress and Future Prospects for Skin‐Attachable Devices for H... | estimate contact properties from tactile images or taxel signals; learn polic... | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 29 | 2021 | Robotic Manipulation and Capture in Space: A Survey | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 30 | 2021 | Integrated linkage-driven dexterous anthropomorphic robotic hand | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 31 | 2017 | Covering a Robot Fingertip With uSkin: A Soft Electronic Skin With Distributed 3-Axis F... | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 32 | 2017 | Robot Collisions: A Survey on Detection, Isolation, and Identification | trigger control or estimation updates on detected events | semantic mismatch between delayed contact observations and current hybrid mode |
| 33 | 2004 | Haptic rendering: introductory concepts | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 34 | 2018 | Toward Haptic Communications Over the 5G Tactile Internet | estimate contact properties from tactile images or taxel signals | whether contact event timing mismatch should be estimated as its own state | task-level... |
| 35 | 2013 | Topography from Topology: Photoinduced Surface Features Generated in Liquid Crystal Pol... | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 36 | 2014 | Learning Neural Network Policies with Guided Policy Search under Unknown Dynamics | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 37 | 2018 | ODAR: Aerial Manipulation Platform Enabling Omnidirectional Wrench Generation | split task space into force-controlled and position-controlled subspaces | semantic mismatch between delayed contact observations and current hybrid mode |
| 38 | 2020 | Variable Impedance Control and Learning—A Review | shape apparent mass-damping-stiffness at the end-effector; learn policy, mode... | semantic mismatch between delayed contact observations and current hybrid mode | how co... |
| 39 | 2011 | Online movement adaptation based on previous sensor experiences | trigger control or estimation updates on detected events | semantic mismatch between delayed contact observations and current hybrid mode |
| 40 | 2006 | Adhesion and friction in gecko toe attachment and detachment | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 41 | 2016 | Transfer from Simulation to Real World through Learning Deep Inverse Dynamics Model | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 42 | 2019 | Large-Area Soft e-Skin: The Challenges Beyond Sensor Designs | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 43 | 2019 | Tactile Image Sensors Employing Camera: A Review | estimate contact properties from tactile images or taxel signals | semantic mismatch between delayed contact observations and current hybrid mode | how ta... |
| 44 | 2006 | A whole-body control framework for humanoids operating in human environments | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 45 | 2015 | 4D Printing with Mechanically Robust, Thermally Actuating Hydrogels | split task space into force-controlled and position-controlled subspaces; tri... | semantic mismatch between delayed contact observations and current hybrid mode |
| 46 | 2012 | Haptic Communications | learn policy, model, or representation from demonstrations or trial data | whether contact event timing mismatch should be estimated as its own state | task-level... |
| 47 | 1995 | Series elastic actuators | introduce a controller, estimator, planner, or analysis for physical interaction | semantic mismatch between delayed contact observations and current hybrid mode |
| 48 | 2023 | A Survey on Deep Reinforcement Learning Algorithms for Robotic Manipulation | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 49 | 2021 | Deep Reinforcement Learning for the Control of Robotic Manipulation: A Focussed Mini-Re... | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
| 50 | 2022 | A soft thumb-sized vision-based sensor with accurate all-round force perception | learn policy, model, or representation from demonstrations or trial data | semantic mismatch between delayed contact observations and current hybrid mode | out-of... |
