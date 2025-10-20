## Benchmarking Empirical Studies on Quantum Software Testing

Note: all the data except `Availability` should be directly collected from the primary paper.

### Basics

temporal trends, publications, How many works include empirical studies

### Empirical studies

+ Objects Under Test: 

  + RQ1 (Adopted programs): What kinds of quantum programs were adopted in the empirical studies?

    (1) Which QPs?  

    (2) Number of programs in one paper
    
  + RQ2 (Buggy versions): 
  
    (1) Number of version in one work (workload). 

    (2) How to generate buggy programs? (Which mutation operators or real-world bug?)

  + RQ3 (Object scalability): 
  
    (1) Whether one paper discusses scalability? 
  
    (2) Settings for qubits, gates, depths. (Fixed/Varied/Adaptive)


+ Comparison:

  + RQ4 (Baselines):

    (1) Whether one paper introduces baselines? 

    (2) What baselines are included?

    (3) How to include? ([Traditional approach]; [Ablation study]; [The state of the art])

  + RQ5 (Comparison method with Baselines):

    (1) p-value

    (2) Effect size

+ Experimental Settings: 

  + RQ6 (Test cases)

    (1) Test inputs

    (2) # of test cases

  + RQ7 (Statistical repeats)

    (1) Shots. 

    (2) Repeats.  

  + RQ8 (Backends)

    (1) Ideal simulator / Noisy simulator / Physical hardware?

    (2) Measurement / Statevector?

+ Evaluation method:

  + RQ9 (Test oracle problem)

    (1) Output expectation: [Specification-based] (explicit); [Mutation-based] (implicit)

    (2) Test oracle: [WOO]; [OPO]

    (3) Statistical methods; [NHT]; [SDM]

  + RQ10 (Evaluation metrics)

    (1) How many works adopt Effectiveness and Cost metrics?

    (2) What Effectiveness and Cost metrics are adopted?

+ Artifact
  + RQ11 (Availability) : 

    (1) Benchmark

    (2) Code