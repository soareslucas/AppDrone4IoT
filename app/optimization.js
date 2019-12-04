//Autonomia em J |||  (59940 - 1500 mAh - 11.1V )   (99900 - 2500 mAh - 11.1V ) (159840 - 4000 mAh - 11.1V )
int Autonomia = 99900

// velocity in m/s
float velocidade = 15

// kg/m^-3
float rho = 1.225

// rad/s
float omega = 20

// cm
float R = 0.5;

// Drone Weight in Newtons
float W = 19;

// Drag Coefficient (zero-lift Drag Coefficient)
float Cd = 0.0225;

// Frontal Area of the UAV  (m2) 
float frontalArea = 0.07992;

// número de sensores + ponto de partida inicial
int nSensores = 20;

range Sensores = 1..nSensores;
int x[Sensores];
int y[Sensores];
int z[Sensores];
float Distancia[Sensores][Sensores];





execute DADOS{

	function calcDistancia(i, j){



		writeln("-----------Início do cálculo:");
		writeln("Sensor " + i + " ("+ x[i]+","+y[i]+","+ z[i]+") "+ " e o  sensor " + j+ " ("+ x[j]+","+y[j]+","+ z[j]+") ");

		var E = 0;
		var D = Opl.sqrt(Opl.pow(x[i]-x[j], 2) + Opl.pow(y[i]-y[j], 2)  + Opl.pow(z[i]-z[j], 2));
		writeln("Distancia:" +D);

		var phi =  Math.asin((  Math.abs(z[i]-z[j] ) / D));
		writeln("Phi: " + phi);

		var Vh =  velocidade * Math.cos(phi);
		writeln("Vh: "+ Vh);

		var Vv =  velocidade * Math.sin(phi);
		writeln("Vv: "+Vv);

		var Pp = (1/2) * rho * Cd * frontalArea * Math.pow(Vh,3)  + ((3.14/4)*4*10*rho*Cd*Math.pow(omega,2)*Math.pow(R,4)) + ((3.14/4)*4*10*rho*Cd*Math.pow(omega,2)*Math.pow(R,4))*3* Math.pow(Vh/omega*R,2);
		writeln("Pp: " + Pp);

		var dividendo =  ( Math.pow(Vh,2)/ (Math.pow(omega,2) * Math.pow(R,2) ) ) + Opl.sqrt( Opl.pow((Math.pow(Vh,2)/ (Math.pow(omega,2) * Math.pow(R,2) )  ),2) - (4* Math.pow(W,2)/ (4* (Math.pow(rho,2)) * Math.pow(3.14,2) * Math.pow(omega, 4) * Math.pow(R,8) ))) ;
		writeln("dividendo: " + dividendo);

		var raiz = dividendo / 2;
		writeln("raiz: " + raiz);

		var lambda =  Math.sqrt((raiz));
		writeln("lambda: " + lambda);

		var Pi = omega*R*W * lambda ;
		writeln("Pi: " + Pi);

		var Ph = Pp + Pi;	
		writeln("Ph: " + Ph);

		var Pv = 0			

		// descending 

		if( (z[i]-z[j]) > 0 ){
			var raizPv = Math.pow(Vv, 2) - (  (2*W)/ (rho *3.14* Math.pow(R,2) ) );
			writeln("Raiz Pv: "+ raizPv);
			if(raizPv < 0){
				var raizPv = Math.pow(15, 2) - (  (2*W)/ (rho *3.14* Math.pow(R,2) ) );
				writeln("Raiz Pv: "+ raizPv);
				Pv = ( (W/2) * 15) - ( (W/2) * Math.sqrt(raizPv) );
			}else{
				Pv = ((W/2) * Vv) - ((W/2) * Math.sqrt(raizPv));			
			}

		} else{		

			// 	climbing
			if( (z[i]-z[j]) < 0 ){
				Pv = ( (W/2) * Vv) + ( (W/2) * Math.sqrt( Math.pow(Vv, 2) + (  (2*W)/ (rho *3.14* Math.pow(R,2) ) ) ) );
			}

		}

		writeln("Pv: "+ Pv);
		E = (D / velocidade) * (Pv + Ph);
	  	return  parseInt(E);
	}





	

	

	function getRandomInt(min, max) {

	    min = Math.ceil(min);

	    max = Math.floor(max);

	    return Math.floor(Math.random() * (max - min + 1)) + min;

	}





for(var s in Sensores){



	



	if(s == 1){



		x[1]= 0;



		y[1]= 0;



		z[1]= 0;



	} else {



		



		x[s]=Opl.rand(1500);



		y[s]=Opl.rand(1500);



		z[s]= getRandomInt(30,100);	



		



	}



	writeln("Sensor " + s +"("+ x[s]+","+y[s]+ y[s] +","+ z[s]+")");



}

	

	

	



	for(var i in Sensores){



		for(var j in Sensores){



			if(i!=j){



				Distancia [i][j] = calcDistancia(i,j);		



			}

			writeln("Energia gasta entre sensor " + i +" e o  sensor " + j +" é "+ Distancia[i][j]+"J");

		}	

	}





}





// Variáveis de Decisão

dvar boolean boleano[Sensores][Sensores];

dvar float+ u[Sensores];



maximize

  (sum ( i in Sensores, j in Sensores: i!= j) boleano[i , j]) - 1 ;

  



subject to {



	forall(j in Sensores)

	  sum (j in Sensores: 1 != j) boleano[1,j]  == 1;





	forall(i in Sensores)

	  sum (i in Sensores: 1 != i) boleano[i,1]  == 1;



	forall(i in Sensores)

		sum ( j in Sensores:  j != i) boleano[j,i]  ==  sum (j in Sensores: i != j) boleano[i,j] ;



	(sum ( i in Sensores, j in Sensores:  i!= j) Distancia[i,j]*boleano[i,j]) <= Autonomia;



// Eliminação de subrotas.

   forall(i in Sensores, j in Sensores: i > 1 && j > 1 && i!= j)

     u[i] - u[j] + nSensores * boleano [i][j] <= nSensores - 1;





};



