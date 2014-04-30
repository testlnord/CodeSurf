
int foo(int a){
	if (a < 2){
		return 1;
	}
	int b = foo(a-1) * a;
	return b;
}

int main(){
	for (int i = 0 ; i < 2; i++){
	    int c = 0;
        for (int j = 4; j  > 1; j-- ){

            if (j % 2){
                int a = foo(j);
                c += a;
            }else {
                c = c * c;
            }
            c --;

        }
	}
	return 0;
}
