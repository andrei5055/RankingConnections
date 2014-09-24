For each my connection I decided to use 
a) the number of his/her total connections as the measure of how active he/she is on LinkedIn
b) the number of our shared connections (see rank_2 in the program and last column in the Output.txt file)  as the measure of how well we know each other.

These parameters are rank_1 and rank_2 in my program and they are in last two columns in the Output.txt file.
I was using 
    rank = rank_1 + 100 * rank_2

Why I chose these parameters? Well, I think that when somebody needs to to rank his/here connections for some practical usage (for instance, for job search or like in your case for sending recommendation regarding some articles), he needs to consider at least two factors:
a) how well this person knows you (and because of that he will be willing to help you with the job search of he will trust your recommendations)
b) how actively he uses LinkedIn (if he is not active, perhaps he will not even see your recommendations or his potential to help you with the job search are limited)

I also considered to use some other parameters, unfortunately I met two following problems:
a) for any person LinkedIn API gives no access to some of these parameters, you could see these parameters for your profile only
b) the fields which are accessible ("specialties", "location", "positions" etc) are either relatively useless (like "location") OR empty for most or the LinkedIn users.

Besides, it would be much harder to implement some NLP analysis for these fields since they are not very well structured and different linked in users treat/fill out them differently. Even the parsing of these fields is a non trivial problem.

