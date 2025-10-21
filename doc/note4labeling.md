# Note for Labels

+ `Basic-Testing4Quantum?`: Whether the paper is a research article that shows a focus on an issue relevant to software testing for quantum systems. 
  + Exclude talks and posters.
+ `Basic-QST&Empirical?`: Whether the paper primarily shows relevance to testing quantum programs/software/circuits and involves empirical studies.
  + We focus on executing the object programs dynamically, thereby excluding formal methods like verification and validation.
  + Debugging, Fault localization, Program repair might fall into this scope.
+ `Basic-PaperScope`:
  + `[Software testing]`: The process of executing a program with the goal of verifying whether its actual behavior conforms to the expected behavior or specifications. 
  + `[Program debugging]`: The activity of identifying and understanding the causes of observed failures or abnormal behaviors in a program.
  + `[Fault localization]`: The process of determining the exact location(s) or code elements that are responsible for the detected fault within a program.
  + `[Program repair]`: The process of modifying the program, often automatically or semi-automatically, to correct the identified fault(s) and restore intended behavior.
+ `Programs-ProgramName`: List the names of all the quantum programs adopted in empirical studies.
  + `[Quantum algorithms: XXX]` refers to the names of concrete programs implementing quantum algorithms. (remark: the name should be offered clearly.) 
  + `[Program source: YYY]` indicates where the programs are selected if provided.
  + `[Artificial programs]` means that the paper randomly generated circuits and adopts a toy example, both of which are not typical quantum algorithms or models.
  + `[QNN systems: ZZZ]` is particularly for quantum neural network benchmarks, where the involved QNNs correspond to specific systems instead of algorithms.
+ `BuggyVersion-GenerationMethod`: The method to generation buggy/target program versions under test
  + `[Mutation operators: XXX]`, where `XXX` could be
    + `Add gate`:
    + `Change qubit` (from ID13): e.g., `H(there)` -> `H(here)`, `CNOT(msg, here)` -> `CNOT(there, here)`, `Entangle(qAlice, qBob)` -> `Entangle(qBob, qAlice)`
    + `Modify condition` (from ID 13): e.g., `M(msg)==One` -> `M(msg)!=One`

  + `[Mutation tooling: YYY]`, direct applied an existing tool for mutation, where `YYY` is the tooling name. 
  
  + `[None]`: The paper does not discuss fault detection (e.g., property testing)
+ `BuggyVersion-#OfVersions`: 
  + `[Mutants: XXX]`: The paper generates numerous mutants. Instead of displaying the performance of each buggy versions, this paper merely examines whether the mutants are killed by the executed test suite.
  + `[Versions: YYY]`: The paper generates several buggy versions, and demonstrates the difference of the approach performances in buggy versions.
  + None: The paper does not discuss fault detection (e.g., property testing)
+ `Scalability-InvolveScalability?`: Whether the paper evaluates how the performance of the proposed approach varies with different scales of the same objects under test.
  + `[N]`: e.g., 5-qubit QFT and 10-qubit BV only;
  + `[Y]`: e.g., 5-qubit QFT and 10-qubit QFT only.
+ `Scalability-#OfQubits`: The number of total qubits of the quantum circuit under test (setting instead of metrics).
+ `Scalability-#OfGates`: The number of quantum gates of the quantum circuit under test (setting instead of metrics).
  + `[Total:XXX]`: The total account of quantum gates if the paper offers this info.
  + `[Specific:YYY]`: The number of specific quantum gates based on the info provided by the paper.
  + This term is not used to evaluate the approach performance, but shows the scalability of the object circuits.
+ `AdoptedBaseline-InvolveBaseline?`: Whether the primary study introduces at least one baseline?
  + The label should be limited to `[Y]` or `[N]`.
+ `AdoptedBaseline-BaselineNames`: The name of adopted baselines.
+ `AdoptedBaseline-InclusionMethod`: The mechanism to include baselines, i.e., `[SOTA competitor]`, `[Ablation study]`, `[Naive approach]`, `N/A`.
  + `[SOTA competitor]`: The state-of-the-art approaches, usually from a recent related study
  + `[Ablation study]`
  + TODO
  + The label should correspond to each of the baseline in `AdoptedBaseline-BaselineNames`.
+ `AdoptedBaseline-InclusionMethod`: 
+ `TestCases-#OfTestCases`: Number of test cases per object under test.
+ `Backends-SimulatorOrHardware`: Which backend is adopted in the paper: `[Ideal simulator]`, `[Noisy simulator]`, or `[Physical hardware]`
  + For the simulator environment without specific clarifications related to quantum noise, we regard it as default `[Ideal simulator]`, because introducing noisy models and dealing with noise should take efforts.
+ `StatiticalRepeats-Shots`:
  + `[Fixed: XXX]`: One fixed value throughout in one experiment of the empirical study
  + `[Adaptive: YYY]`: Configuration adaptive to arguments like the number of qubits
  + `[Varied: ZZZ]`: Attempt several shots in the same experiment of the empirical study but their values are independent of other arguments 
  + `N/A`: This appears if `Backends-OutputType` is [state vector]
+ `TestOracle-OutputExpectation`:
  + `[Original program output]`: The expected outputs are the ones from the original program that the mutants are generated from.
  + `[Program specification: Probability]`: Using the program specification in the form of distribution of classical bits or integers. (including the bit string `01100`)
  + `[Program specification: Formula]`:  Using the program specification expressed by the mapping between state vectors or density matrices.
  + `[Proposed property: Metamorphic relation]`: A **metamorphic relation (MR)** defines an expected relationship among multiple executions of a program, typically between two related inputs and their corresponding outputs. A program’s behavior can be regarded as *consistent with its expected property* if the MR is satisfied. However, satisfying an MR does not guarantee that the program output—or the program itself—is absolutely correct; it only indicates that no fault has been revealed under this MR.
  + `[Proposed property: General property]`:  This property checks whether a program satisfies a given *general property* that specifies its expected behavior, rather than a specific metamorphic relation. Such properties can describe invariants, input-output constraints, or behavioral rules that the program should hold under all valid inputs.
+ `TestOracle-OracleName`:
  + `[Wrong output oracle]`: Refer  to Shaukat et al. "assessing ..."
  + `[Output probability oracle]`: Refer  to Shaukat et al. "assessing ..."
  + `[Dominant output oracle]` (first named in our work): Summarized from *Paper 15*. Give the metric Probability of Successful Trail (PST) for measuring the reliability of single-output quantum circuits, i.e., Number of Successful Trails / Total Number Of Trails. To identify the correct output while using PST, the probability of each incorrect output should be less than PST. In other words, the correct output should be the most frequent output pattern.
  + `[Property-based oracle]`: The test passes if a specified property or invariant of the program is satisfied, rather than matching an exact expected output.
+ `TestOracle-OracleImplementation`: Statistical methods to give the test results
+ TODO

