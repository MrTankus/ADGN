# ADGN
ADGN stands for Adhoc Dynamic Geometric Network.<br/>
This library uses a genetic algorithm to optimize a spatially embedded
network where every vertex has a geometric constraint.

<h3>Running the GA</h3>
The GA loads the geometric constraints (i.e. Interest Areas) from a
given path. (the file is json format with a specific schema provided
in the schemas folder). Then an initial random population is generated
and the GA evolution process begins.
<h4>Parameters</h4>
<ul>
<li><b><i>--interest-areas</i></b> (required): the path to the json file containing the interest areas</l1>
<li><b><i>--fitness-function</i></b> (required): the fitness function for the GA.
    <ul>
    <li><b><i>1</i></b>: sum of the connectivity componenets squared - optimum is max</li>
    <li><b><i>3</i></b>: harmonic average of all path length - optimum is min</li>
    </ul>
</li>
<li><b><i>--output-base-dir</i></b> (required): the directory for the GA to output its results including statistics and process visualization</li>
<li><b><i>--initial-population</i></b> (optional. default 10): the size of the initial population generated by the GA</li>
<li><b><i>--generations</i></b> (optional. default 300): how many generation should the GA iterate</li>
<li><b><i>--mutation-factor</i></b> (optional. default 1): the probability [0,1] of mutation in the GA process. 0 will never mutate, 1 will always mutate.</li>
<li><b><i>--visualize</i></b> (optional. defatul false): if the GA process should output visualizations of the GA process and its statistics</li>
<li><b><i>--parallel</i></b> (optional. default false): should the GA use multiple processes to parallelize computation</li>
</ul>

<h4>Examples</h4>
The following command will run the GA<br/>
<i>python adgn.py --interest-areas=ia.json --fitness-function=3 --output-base-dir=/tmp/simulations --parallel=true --visualize=true</i>


<br/>
<h3>Generating random Interest Areas</h3>
To generate a interest areas json file with random interest areas, please use the following command<br/>
<i>python ia_generator.py --amount=170 --xlim=8 --ylim=8 --output=/tmp/interest_areas.json</i> 
<h4>Parameters</h4>
<ul>
<li><b><i>--amount</i></b> (required): the amount of interest areas to generate</li>
<li><b><i>--xlim</i></b> (required): the absolute value of the limit of the x axis on the [xy] plane</li>
<li><b><i>--ylim</i></b> (required): the absolute value of the limit of the y axis on the [xy] plane</li>
<li><b><i>--output</i></b> (required): the file name (with path) to output the generated interest areas json file</li>
<li><b><i>--allow-overlap</i></b> (optional. default false): can the interest areas overlap</li>
<li><b><i>--show</i></b> (optional. default true): if set to true, at the end of the process, will show the generated interst areas on the [xy] plane</li>
</ul> 
The interest areas will be generated in the rectangle [-xlim, xlim] X [-ylim, ylim]

<h4>Known issues</h4>
if the <i>--allow-overlap</i> is set to false, the interest areas random generator may result in an infinite loop. to
avoid this, please set the <i>--xlim</i> and <i>--ylim</i> parameters to large enough values.

<h3>Logging</h3>
Every log will output to the stdout.