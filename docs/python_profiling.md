# Python Profiling

I've seen a few posts on Hacker News recently about writing fast and efficient code. Fortunately this example was written in Python which is probably the language that could save the most instruction cycles globally with a bit of optimization. I say this because Python is ubiquitous when it comes to writing prototype scripts that eventually get pushed to production under project deadlines.

The rule of thumb that I use, and remind my coworkers is that the order of code optimization is:


1. Make it work - optimize for business functionality (MVP)
2. Make it right - optimize for human readability (documentation, test cases, extendable)
3. Make it fast - optimize for execution speed 

In the work of data science, the opportunities to get to the third stage are rare enough that they aren't covered in many learning materials but important enough that you need to know them. In this post i'll cover the profiling basics when using Python.

Be aware that many profiling results are dependent on the current state of the computer running the profiler, it's best to run each result several times to normalize across background processes that may be happening.


## %timeit

For those using Jupyter notebooks or an iPython environment, %timeit is the easiest way to start measuring execution time of functions and therefore being able to compare speeds of different solutions.

``` py title="timeit"
%timeit [i**3 for i in range(100)]
#100000 loops, best of 5: 12.1 µs per loop
```
## %memit

memit is the easiest way to start memory profiling in a Jupyter Notebook or iPython environment.
``` py title="memit"
! pip install memory_profiler
%load_ext memory_profiler
%memit (i**3 for i in range(10000))
%memit [i**3 for i in range(10000)]
```


## /usr/bin/time

/usr/bin/time is a unix utility to time the execution of any program. It doesn't have as much detail as the python specific profilers but can be used for all types of programs that run as a unix CLI.
``` bash
/usr/bin/time curl https://matthewburke.xyz >> /dev/null 
```


## cProfile

cProfile is part of the standard library and will show you the time spent in each function of a certain program.
``` bash
python -m cProfile -s cumulative script.py
python -m cProfile -s cumulative script.py | grep script.py 
```



## line_profiler

Once you've worked out which function is using up the most CPU resources you can dive in deeper and investigate which line is using the most CPU resources with line_profiler. To run this you'll need to download the pip package line_profiler, add the @profile decorator to the functions you want to profile and finally run the line_profiler from the command line 

``` py title="function_to_profile.py
@profile
def slow_add(a: int, b: int) -> int:
    time.sleep(1)
    return a+b

```

``` bash
kernprof -l function_to_profile.py
```

See the [github repo](https://github.com/pyutils/line_profiler) github repo for more information.

## memory_profiler

The memory_profiler works in much the same way as the line_profiler. Have a look at the [official documentation](https://github.com/pythonprofilers/memory_profiler) to get started. 




## py-spy

py-spy (note the hyphen) is an incredible piece of work which allows you to profile a python process as it is running without slowing down the process (too much). You can imagine how useful it would be when trying to determine what the bottleneck is for a web server when serving real traffic. You can find more information on the [github repo](https://github.com/benfred/py-spy).
