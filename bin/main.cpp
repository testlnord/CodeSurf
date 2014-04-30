
int foo(int a){
	if (a < 2){
		return 1;
	}
	int b = foo(a-1) * a;
	return b;
}

int main(){
//    int *k = new int;
//    delete k;
//    delete k;
	int a = foo(3);
	for (int i = 0 ; i < 2; i++){
        for (int j = a; j  > 2; j-- ){
            int c = 2;
            c = c * c;
            j --;
        }
	}
	return 0;
}
