
sig System
{
}

sig Processor
{
	system : one System
}

sig Kernel
{
	system : lone System,
	processors : set Processor
}

fact KernelScope
{
	#Kernel = 1
}

fact SytemScope
{
	all s : System | some k : Kernel | s in k.system
}

fact ProcessorScope
{
	all p : Processor | all k : Kernel | p in k.processors
}

fact ProcessorLifetime
{
	all p : Processor, k : Kernel | p.system = k.system
}



