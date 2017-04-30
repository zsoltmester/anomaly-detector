for (( i = 0; i < 9999; i++ )); do
	python detect_anomaly.py --training ~/big-data-repository/milano/cdr/2013-11 --testing ~/big-data-repository/milano/cdr/2013-12 --square $i --action save
done
