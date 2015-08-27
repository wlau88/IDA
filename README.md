# Instagram Demographics Analysis (IDA)
Warren Lau, August 2015

# Contents
* [TL;DR](#tldr)
* [Overview](#overview)
* [Model](#model)
* [Caffe](#caffe)

# <a name="tldr"/></a>TL;DR
Instagram Demographics Analysis (aka IDA) allows you to visualize the geospatial pattern of basic demographic groups (age and gender) on a map. Using computer vision methods, IDA enriches publicly available Instagram metadata with age and gender predictions based on users pictures. You can then understand your demographics' offline behavior at scale geospatially.

# <a name="overview"/></a>Overview
With over 200M users and 20B photos, Instagram is one of the most popular photo-sharing platform for millenials. Businesses are interested in this [demographic](http://www.wired.com/2013/04/genwired/) because they tend to be more tech-savvy and provide tremendous value for [O2O](http://venturebeat.com/2015/07/06/want-to-see-the-future-of-the-o2o-economy-look-east/) (online to offline) integration, one of the most important and discussed factor for businesses today.

This is the motivation behind IDA. By generating a map visualization of different gender and age group - the most basic demographics information - over a geospatial area, users can understand where certain demographic groups are at any time of the day, or at an aggregate time period. 

However, age and gender information are not publicly available. With images being the predominant media on instagram, the most direct approach is to predict the gender and age of users with their profile picture and pictures they are tagged in. To obtain this information, two pieces of machine learning methods are used. Haar Cascade Classifiers to detect the presence of a face and Convolutional Neural Networks to predict the age and gender of the face, which are discussed more in the [model](#model) section. 

IDA provides 2 main use cases for businesses and governments:

* **Sales and Marketing**: Say you're a growing business and you've identified an area that is densely populated with older females that are extremely engaged on Instagram that you call the ["Kardarshians"](https://instagram.com/kimkardashian/). They represent one of your most valued customer segment. You can use IDA to 1) see if there is another area that is also densely populated with the Kardashians to open a new store, 2) see your performance in other areas that are also densely populated (may be performing worse because losing customers to competitors in the area or demographics shifting), or 3) see where are the more densely populated area and increase promotional activities at a particular time of day that is the most densely populated. 

* **Asset Management**: Say you're responsible for regional planning for your local government and you've identified a park in your area that are frequently visited by men that are using the park as a workout spot. You can plan your maintenance accordingly and upkeep the recreational space.

###Map Visaulizations:

![Gender map viz](https://raw.githubusercontent.com/wlau88/IDA/master/imgs/gender_map.png?token=AKfYrqO0i2XXZrKm5M6k5u41Z4YLPlWQks5V52lVwA%3D%3D)  

![Age map viz](https://raw.githubusercontent.com/wlau88/IDA/master/imgs/age_map.png?token=AKfYrtbCar6-iKl_XvkBospnX-2SqBpHks5V52kOwA%3D%3D)

###Examples:

####Marina: Girls dancing at bars

![Marina Slide](https://raw.githubusercontent.com/wlau88/IDA/master/imgs/marina.png?token=AKfYrreddDjJRRoNZYfTCcLKacSC_68Vks5V52mPwA%3D%3D) 

####Castro: Guys getting bubble tea

![Castro Slide](https://raw.githubusercontent.com/wlau88/IDA/master/imgs/castro.png?token=AKfYrrj-GnaOVxbZncoZiaz3YXHLpUeWks5V52k8wA%3D%3D)

# <a name="model"/></a>Model
This project uses two main machine learning methods - Haar Cascade Classifiers and Convolutional Neural Networks (CNNs), each on a different library, OpenCV and Caffe. Since the installation of both these packages can be tedious, the recommended approach is to use the following AMI [Deep learning Torch7 and Caffe v2 (ami-027a4e6a)] with both of these package installed.

####Overall Data Pipeline
The overall data pipeline follows the Extract-Transform-Load (ETL) process:

#####Extract:
Download the locations of interest and the corresponding images metadata using `instagram_metadata.py`. Your API key information should be in the `api_key_tokens` folder. These location_id's and images metadata would be stored in the `location` and `metadata` mongodb tables.

#####Transform:
Transform the images metadata and enrich them with age and gender predictions. Use the `age_gender_extractor.py` (takes a list of metadata_id's) or `age_gender_extractor_in_memory.py` (takes a list of metadata, faster performance). 

Under the hood, they are using `image_classifier.py` and `caffe_classifier.py` to do the age and gender predictions. Note that `image_classifier` is primarily responsible for preprocessing and cropping the face and `caffe_classifier` for the age and gender predictions. This allows the two components to be decoupled and tuned separately. As an aside, `model_tuner.py` would help you tune the Haar Cascade Classifiers with a customed implementation of Grid Search.

#####Load:
The age and gender predictions from the Transform step would be placed intermediarily in mongodb before getting summarized and loaded into postgresql. To create the age and gender predictions for each user_id table, i.e. ``user-age-gender-table`` aka uag_table, use `uag_table.py`; as for the location activities table, i.e. ``photo_id-lat-lng-user_id-action-time-table`` aka plat_table, use `plat_table.py`.

Now you have the two tables for the visualization!

####Visualization (Viz)
The R script `create_map_viz.R` to generate visualization is in the `viz` folder. To visualize your results, download the joined sql table from the above to a `.csv` file, and see your geospatial demographics information come to life!

####Machine Learning / Computer Vision Methods
-
####Haar Cascade Classifiers
The Haar Cascade Classifiers used are created by Viola and Jones, and further improved by Lienhart et al. The details can be found on the [OpenCV website](http://docs.opencv.org/modules/objdetect/doc/cascade_classification.html).

At a high level, there are 2 primary components in the Haar Cascade Classifiers, the learning algorithm and the cascade architecture, they work this way (refer to the Viola-Jones paper for notations):

![Learning](https://raw.githubusercontent.com/wlau88/IDA/master/imgs/learning.png?token=AKfYrrTDapeeuw_InVfQsoTWske873WNks5V52l3wA%3D%3D)

![Cascade](https://raw.githubusercontent.com/wlau88/IDA/master/imgs/cascade.png?token=AKfYrg7MX49K9Vr9sBSeIup-3LoTW4qTks5V52kmwA%3D%3D)

####Convolutional Neural Networks (CNNs)
The Age and Gender CNNs used are architected and trained by Gil Levi and Tal Hassner. The details can be found on their [website](http://www.openu.ac.il/home/hassner/projects/cnn_agegender/). 

At a high level, the Gender CNN works this way: 

![CNN age](https://raw.githubusercontent.com/wlau88/IDA/master/imgs/CNN.jpg?token=AKfYrivi6t9n8Km-gJDfhZRmqPrhbWAsks5V52jxwA%3D%3D)

The Age CNN works similarly. 

# <a name="caffe"/></a>Caffe
Caffe is one of the most robust deep learning package, and is the platform where the Gil and Hassner's Age and Gender CNNs are built on. In order to get better age and gender prediction results, additional instagram images are used to fine-tune the Age and Gender CNNs. Due to the limited time available, 357 images are hand labeled with age [ labels: '(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)' ] and gender [ labels: 'Male', 'Female' ] information. 25% (90 images) are used in the validation set to get the accuracy score and 75% (267 images) are used in the training set to fine-tune the CNNs. The results are [below](#tuning).

To prepare your images for the CNNs on Caffe, you would need to convert the images into lmdb files to be passed into Caffe. 

Here are the steps: 

* Group them in a training and a validation folder. Caffe will tune on the images in the training folder and measure its accuracy on the images in the validation folder. If you want to resize the images yourself, they would need to be 256x256x3 jpeg files. If not, the following script in the next step would resize the images for you if you set ``resize=true``.

* For each set (training and validation), create a text file specifying the categories that the pictures belong to, like below, where imgabc.jpg belongs to category 0, imgdef.jpg belongs to category 1, etc. For the Gender CNN, 'Male' corresponds to 0 and 'Female' 1. For the Age CNN, '(0, 2)' corresponds to 0, ('4, 6') to 1 and so on.

> imgabc.jpg 0  
> imgdef.jpg 1  
> imgghi.jpg 2  

* Check `create_lmdb.sh` and ensure that your folders are aligned with the arguments (or change the arguments). Run the script. This will create the training and validation lmdb directories. Caffe will work with them from now on.

* On to Caffe. Depending on how many iterations you want to run, what hyperparameter values you want to set, modify the `solver.prototxt` in the `caffe_prototxt` folder accordingly. The net configuration `train_val.prototxt` is also there. Once you have it configured, locate the caffe binary file, solver.prototxt, and the trained .caffemodel and run the following:

```
{path to caffe binary file} train -solver {path to solver.prototxt} -weights {path to .caffemodel} -gpu 0
```

* Sit back, relax and see how the fine-tuning is happening and accuracy improving!


## <a name="tuning"/></a> CNNs Tuning
It turns out that the number of iterations that would result in the highest accuracy for tuning on the Gender Net was 300; and for the Age Net - given the inherent difficulty of the task and hand labeling to conform with the age buckets - no tuning results in the highest accuracy.

The complete results are shown below.
 
###Gender Net 
####0 Training/Tuning Iterations (No Tuning)
```
I0825 23:57:18.866293  8119 solver.cpp:246] Iteration 0, loss = 0.750021 
I0825 23:57:18.866374  8119 solver.cpp:264] Iteration 0, Testing net (#0)
I0825 23:57:29.431041  8119 solver.cpp:315]     Test net output #0: accuracy = 0.6874
I0825 23:57:29.431110  8119 solver.cpp:315]     Test net output #1: loss = 0.998023 (* 1 = 0.998023 loss)
```
####100 Training/Tuning Iterations
```
I0826 00:07:56.853926 13560 solver.cpp:246] Iteration 100, loss = 0.0578998
I0826 00:07:56.853991 13560 solver.cpp:264] Iteration 100, Testing net (#0)
I0826 00:08:07.377655 13560 solver.cpp:315]     Test net output #0: accuracy = 0.7182
I0826 00:08:07.377727 13560 solver.cpp:315]     Test net output #1: loss = 0.883332 (* 1 = 0.883332 loss)
```
####200 Training/Tuning Iterations
```
I0826 01:52:28.946671  1615 solver.cpp:246] Iteration 200, loss = 0.00628766
I0826 01:52:28.946735  1615 solver.cpp:264] Iteration 200, Testing net (#0)
I0826 01:52:39.415439  1615 solver.cpp:315]     Test net output #0: accuracy = 0.7408
I0826 01:52:39.415577  1615 solver.cpp:315]     Test net output #1: loss = 1.24991 (* 1 = 1.24991 loss)
```
####300 Training/Tuning Iterations (Best)
```
I0826 00:42:43.673614 31064 solver.cpp:246] Iteration 300, loss = 0.132172
I0826 00:42:43.673671 31064 solver.cpp:264] Iteration 300, Testing net (#0)
I0826 00:42:54.145483 31064 solver.cpp:315]     Test net output #0: accuracy = 0.7652
I0826 00:42:54.145624 31064 solver.cpp:315]     Test net output #1: loss = 1.29343 (* 1 = 1.29343 loss)
```
####400 Training/Tuning Iterations
```
I0826 01:27:54.896600 20698 solver.cpp:246] Iteration 400, loss = 0.00598166
I0826 01:27:54.896662 20698 solver.cpp:264] Iteration 400, Testing net (#0)
I0826 01:28:05.351300 20698 solver.cpp:315]     Test net output #0: accuracy = 0.7014
I0826 01:28:05.351371 20698 solver.cpp:315]     Test net output #1: loss = 1.34579 (* 1 = 1.34579 loss)
```
####500 Training/Tuning Iterations
```
I0826 00:18:59.477177 17886 solver.cpp:246] Iteration 500, loss = 0.000154082
I0826 00:18:59.477238 17886 solver.cpp:264] Iteration 500, Testing net (#0)
I0826 00:19:09.942698 17886 solver.cpp:315]     Test net output #0: accuracy = 0.7066
I0826 00:19:09.942766 17886 solver.cpp:315]     Test net output #1: loss = 1.53052 (* 1 = 1.53052 loss)
```

###Age Net 
####0 Training/Tuning Iterations (No Tuning, Best)
```
I0826 18:22:11.466423  2049 solver.cpp:246] Iteration 0, loss = 1.8762
I0826 18:22:11.466497  2049 solver.cpp:264] Iteration 0, Testing net (#0)
I0826 18:22:22.007977  2049 solver.cpp:315]     Test net output #0: accuracy = 0.5614
I0826 18:22:22.008047  2049 solver.cpp:315]     Test net output #1: loss = 1.37746 (* 1 = 1.37746 loss)
```
####100 Training/Tuning Iterations
```
I0826 18:20:10.581392   386 solver.cpp:246] Iteration 100, loss = 0.305899
I0826 18:20:10.581455   386 solver.cpp:264] Iteration 100, Testing net (#0)
I0826 18:20:21.096061   386 solver.cpp:315]     Test net output #0: accuracy = 0.4782
I0826 18:20:21.096130   386 solver.cpp:315]     Test net output #1: loss = 2.08833 (* 1 = 2.08833 loss)
```
####200 Training/Tuning Iterations
```
I0826 18:24:43.244787  2686 solver.cpp:246] Iteration 200, loss = 0.0439556
I0826 18:24:43.244848  2686 solver.cpp:264] Iteration 200, Testing net (#0)
I0826 18:24:53.728013  2686 solver.cpp:315]     Test net output #0: accuracy = 0.4774
I0826 18:24:53.728157  2686 solver.cpp:315]     Test net output #1: loss = 2.84672 (* 1 = 2.84672 loss)
```
####300 Training/Tuning Iterations
```
I0826 18:28:24.683991  4634 solver.cpp:246] Iteration 300, loss = 0.0889525
I0826 18:28:24.684051  4634 solver.cpp:264] Iteration 300, Testing net (#0)
I0826 18:28:56.219703  4634 solver.cpp:315]     Test net output #0: accuracy = 0.4328
I0826 18:28:56.219802  4634 solver.cpp:315]     Test net output #1: loss = 3.1341 (* 1 = 3.1341 loss)
```
=======
# IDA
Instagram Demographics Analysis (IDA)
>>>>>>> 3db370785b70aeedc4742d4b534035627c1f95de
