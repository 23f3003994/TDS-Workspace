import math

T = 20
p=0.8200
n_test=500

sigma = math.sqrt(p*(1-p)/n_test )    #std dev  

inflation = sigma * math.sqrt(2* math.log(T) )  
expected_inflation_pp=inflation*100

adjusted_accuracy = (p * 100) - expected_inflation_pp

print(f"{sigma:.6f},{expected_inflation_pp:.3f},{adjusted_accuracy:.3f}")

