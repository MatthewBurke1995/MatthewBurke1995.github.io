# Unix Named Pipes

## Message Queues

Message queues are an architectural pattern to decouple the process of gathering tasks and resolving tasks. There are a couple of reasons why you would use this design pattern. It might not be possible to complete the task within a single request reply loop or it might be easier to resolve tasks in a batch method due to large initial process startup costs.

Assuming that the process that resolves the work is different to the one that gathers the work (i.e. is a message queue and not a task queue) then this is also a form of interprocess communication. Other options for interprocess communication could be JSON over HTTP (for processes across servers), shared memory such as Redis or the filesystem for processes that run on the same server.

## Unix Pipes

In unix everything is a file, including pipes. As a brief review pipes are a way of turning stdin (read as "standard input") to stdout ("standard output"). The following script uses `cat` which takes a file or several files from stdin and prints to stdout. The pipe in the middle takes that stdout and converts it to stdin for the next process which is also cat and prints the text to stdout. 'cat' converts stdin to stdout and the pipe converts stdout to stdin, together they act like the identity function for any text. The following two commands do the same thing.

``` sh
cat book.txt        
cat book.txt | cat  
```

😮‍💨 that was a lot to parse out. Pipes are powerful and efficient when each process can handle the data as a stream. We can compare the time taken to run a pipe of 20 cats versus the time taken to run a pipe of one cat.

``` sh 
time cat book.txt                       #...  0.007 total
time cat book.txt | cat | 🐱x20 | cat   #...  0.021 total
```

More processes means more processing but there is a lot of time saved when you dont have to read from the file system each time. We could also create a strange pipe by using cat if we save the stdout to an intermediate file and then read that file as the stdin for the next process, this takes roughly twice the time and also twice the cpu power as the unix pipe version.

``` sh
cat book.txt > tempfile; cat tempfile > tempfile ; cat tempfile > tempfile;...
```

Writing to files is always an option, there is a huge overlap between pipes and files in terms of functionality. But one reason why files aren't appropriate is when we want to make sure that each line is processed exactly once even if several processes are accessing the content.

## Unix Named Pipes as a Message Queue

Unix has a feature called 'Named Pipes' where we can give a pipe a name, let it persist in the file system. Unlike regular pipes named pipes can persist over time, and unlike regular files they have the guarantee that each line will only be processed once.

``` sh title="named pipes in bash"
mkfifo newnamedpipe
echo "hi" > newnamedpipe

#open up new terminal
cat newnamedpipe #output of "hi"
cat newnamedpipe #no output, waiting for new message to join queue.

```


``` python title="Read and write to named pipes in Python"
import os
PIPE_NAME = "my_named_pipe"

def write_named_pipe(pipe_name,message):
  # Create the named pipe if it does not exist
  if not os.path.exists(pipe_name):
    os.mkfifo(pipe_name)
  # Open the named pipe
  with open(pipe_name, "w") as pipe:
    # Write the message to the pipe
    pipe.write("Hello, other process!")
    pipe.flush()

def read_named_pipe(pipe_name):
  # Open the named pipe for reading
  with open(pipe_name, "r") as pipe:
    response = pipe.read()
    print(response)

```


## Wrap up
You can use named pipes as a very simple message queue on any unix distribution.
