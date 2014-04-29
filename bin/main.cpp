
int foo(int a){
	if (a < 2){
		return 1;
	}
	int b = foo(a-1) * a;
	return b;
}

int main(){
	int a = foo(3);
	while (a > 2 ){
        int c = 2;
        c = c * c;
        a --;
	}
	return 0;
}
