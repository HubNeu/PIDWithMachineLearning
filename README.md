# PIDWithMachineLearning
This is the result of almost 2 months of work for my intelligent control systems class, where we built some container filling and mixing simulations and then I tried to apply machine learning algorithms (gradient descent and genetic algorithm) to find the best parameters for the PID controller. Works, sort of.

Tech used:
-python 3.9.1
-tensor flow 2.4.1
-deepevolution (0.0.4 *I think*)

Project structure:
-jupyterProjects is the folder containing everything I've written in jupyter notebook to teach the net. MLPID is linear regression on tensor flow, GAPID is genetic algorithm using deepevolution wrapper for tensorflow's keras.
-programs is the folder containing scripts I've written in pycharm (only one that was actually needed here, but there were more parallel to it)

Introduction:
  This is the project containing everything I did for my Intelligent Control Systems class. The main problem I tackle here is the filling problem, mixing is additional, less important:

filling process:<br />
![image](https://user-images.githubusercontent.com/49408414/120939845-45db2900-c71a-11eb-9d00-b547afffe7b6.png)<br />
![image](https://user-images.githubusercontent.com/49408414/120939849-4e336400-c71a-11eb-8c8b-362b368c5df6.png)<br />
![image](https://user-images.githubusercontent.com/49408414/120939882-7b801200-c71a-11eb-94a8-90d4b99e8953.png)<br />
![image](https://user-images.githubusercontent.com/49408414/120940046-6e175780-c71b-11eb-845f-f87558df5b43.png)<br />

mixing process:<br />
![image](https://user-images.githubusercontent.com/49408414/120939820-22b07980-c71a-11eb-837d-1287a98849ad.png)<br />
![image](https://user-images.githubusercontent.com/49408414/120939866-61deca80-c71a-11eb-8f0e-e6a1fb20eff5.png)<br />

  Since the math problem was already defined (I was given the equations to run), I *only* had to implement the PID controller and the machine learning part. PID controller was simple. The other was not (btw, I only did machine learning system for filling.py, not mixing.py). It went like this:
  
  I had only 3 input parameters that I could reliably use: Area (of the bottom of the container, in m^2), Beta (in m^(5/2)/s) and Tp (step time (in seconds)). Beta is *almost* flow in meters^3 per second. Almost, bc in order to actually be that flow, then it has to be multiplied by sqrt(water_level). The important part is, that is behaves like a constant: when the number gets smaller, it flows out less as if it was more dense, the bigger, the less dense and faster flowing it gets.
  
  Having only these 3 parameters, I decided to generate many different combinations of parameters that it would compute (A, Beta, Tp, P, I, D). Each of those had 20 values in a certain (useful) range. This came out to 40 million combinations! This is also where my first mistake happened. When generating the D parameter, I gave it a useful step of 0.4, which waaaaay too much. It should've been somewhere around 0.05 to 0.1. Because of this, the ALL values in the training set were 0.4. Not good.
  
  Anyway, now my poor pc had to simulate them all. Because I didn't want to waste time with simulating using GPU, I used multiprocessor library, to have 10 parallel processes all acting on and saving to different files, so they wouldn't collide.
  
  Unfortunately, this is where the second mistake lies: I saved parameters to different files OUT OF ORDER, which means that I had to collect them together and sort after the simulation has finished, before I could move to choosing the best ones. SortedData1 and sortedDataTop5 contain top 1 and 5 (respectively). Even top 1 contains 250k examples, so it's plenty for our nets.
  
Moving to training neural nets, first linear regression version:
I decided for and 80-20 split. That gave me 191786 train examples. This is a plot of all the data I got:
![image](https://user-images.githubusercontent.com/49408414/120940469-bfc0e180-c71d-11eb-9315-8cf818e74535.png)

Not much useful info, but we still could plot a nice line through the middle though. We go on with normalization and then move to our net definition:
![image](https://user-images.githubusercontent.com/49408414/120940914-06afd680-c720-11eb-9610-a3947939ddd8.png)
I probably could've used 3 inputs straight into 3 outputs adn get the same output. Anyway, I got absolute error of 1.31 and square error of 4.92:
![image](https://user-images.githubusercontent.com/49408414/120941140-5fcc3a00-c721-11eb-91fc-d3bd1b8ece15.png)
And here are the plots:\n
![image](https://user-images.githubusercontent.com/49408414/120941209-b8033c00-c721-11eb-8cff-7cf6cbcb7df5.png)
![image](https://user-images.githubusercontent.com/49408414/120941240-d6693780-c721-11eb-8c87-38f126863ce5.png)
![image](https://user-images.githubusercontent.com/49408414/120941259-e6811700-c721-11eb-983a-e58a0717c207.png)
![image](https://user-images.githubusercontent.com/49408414/120941288-0fa1a780-c722-11eb-8c87-f1cf17939319.png)
I don't think I need to comment on the effectiveness of this, do I?

Suprisingly, the values we get from this model are quite usable. They were certainly better than anything I could come up with for a system with parameters [10, 1.3 1] where the net's results achieved 99% accuracy in 91 seconds and it took my best settings a 150 seconds. It's certainly better than nothing at all, but it's probably not optimal. 

For the genetic algorithm's model:
Due to a bit different way it was defined, it looked like this:
![image](https://user-images.githubusercontent.com/49408414/120941514-678cde00-c723-11eb-8ee4-2c35fa703c3b.png)
We then train it for 500 generations (usually we get the best result after ~350 generations) in populations of 100, from which we choose top 3 achievers. The used fitness function looks like this:
![image](https://user-images.githubusercontent.com/49408414/120941596-bc305900-c723-11eb-9dfc-39777ca39791.png)
We evalute the model (assign a score to the model, score is smaller the better the model, and we need an inverse, so then we perform just that:
final_score = 1/score\*1000
Teaching the model:
![image](https://user-images.githubusercontent.com/49408414/120941751-c2730500-c724-11eb-82c5-dd1481ebc978.png)
The actual values we get from this model are very simmilar, just slightly worse.
