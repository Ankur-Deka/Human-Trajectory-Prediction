1)TRAINING 
  
  	(if training dataset is 5, epoch is 26)

	a)	train.py saves model in:
			srnn-pytorch/save/trainedOn_5/save_attention'
		config.pkl stores parser arguments
		srnn_model_26.tar stores the trained pytorch model

	b)	train.py also logs training information in srnn-pytorch/log/trainedOn_5/log_attention

2)TESTING/SAMPLING

	(if training dataset is 5, testing dataset is 6)
	
	a) sample.py saves result in:
		srnn-pytorch/save/trainedOn_5/testedOn_6

Updates:
1) v1 - New attention, much better result than the original formulation 
2) v2 - GLobal obstacle map, not much improvement. New attention code needs to be changed
3) v3 - a) Relative displacements at single time steps
	b) RNNs are fed with disp aligned to pedestrians last motion step
	c) New attention code needs to be changed
4) v4 - a) All changes mentioned in v3
	b) Removed Gaussian
