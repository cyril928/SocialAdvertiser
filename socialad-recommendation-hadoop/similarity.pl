use WordNet::QueryData;
use WordNet::Similarity::path;
use List::Util qw[min max];

$wn = WordNet::QueryData->new;
$measure = WordNet::Similarity::path->new ($wn);

open AmazonFile, "<", "./Amazon" or die $!;
my @amzCategories = <AmazonFile>; #the list of all amazon categories
close AmazonFile;

open FB, "<", "./FBcategory" or die $!;
open Score, ">", "./Score" or die $!;

while ($FBCategory = <FB>) 
{
  print $FBCategory;
  chomp($FBCategory); #avoid \n at the end of the string
  my @scoreVector; #socre vector of a FBCategory
  my @FBSubCategories = split(/\//, $FBCategory);
	foreach my $amzCategory (@amzCategories){
	  my $max = 0;
	  my @amzSubCategories = split(/\//, $amzCategory);
	  foreach my $FBSubCategory (@FBSubCategories){
		my @senses = $wn->querySense($FBSubCategory);
		foreach my $sense (@senses){
		  foreach my $amzSubCategory (@amzSubCategories){
			my $value = $measure->getRelatedness($sense, $amzSubCategory);
			my ($error, $errorString) = $measure->getError();
			die $errorString if $error;
			if ($value == 1) {
			  $max = 1;
			  last if ($max == 1);
			}
			if ($value > $max) 
			{$max = $value;}
		  }
		last if ($max == 1);
		}
		last if ($max == 1);
	  }
	  $roundValue=int(($max+0.005)*100);
	push(@scoreVector,$roundValue/100);
	}
	print Score "@scoreVector"."\n";
}

close FB;
close Score;
