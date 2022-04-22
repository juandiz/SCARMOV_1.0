V1 25.03.2021

	- En esta primera version se establece la organización general de la GUI. Podemos controlar al robot mandando
	coordenadas en 3D desde el origen de la base del escara.
	- El robot movil tambien se puede controlar con los 5 botones centrales
	- Tenemos un cuadro que nos indica el estado en el que nos encontramos

V2 10.04.2021

	- Agregamos ahora mas funcionalidades que incluyen la visualización del angulo que corresponde a la articulación.
	- Incluimos la posibilidad de agregar velocidades angulares simulando movimiento con libreria Time
	- Corregimos errores en cálculo angular.
	- Aún hay ciertos valores que arrojan incoherencias en las coordenadas. 

V3 27.04.2021

	- Se incluye un plano XY que sirva para indicar las coordenadas del robot.
	- Corregimos algunos errores matemáticos y mejoramos vizualización de estados.
	- Implementación de errores

V4 y V5 02/05/21

	- Incluimos el calculo de trayectoria con el numero de puntos variable
	- La trayectoria es en linea recta
	- Evitamos puntos que esten fuera de rango
	- Problemas en el cuadrante 3  

V6  03/05/21

	- Mejora en errores de la funcion de calculo de cinemática inversa
	- Mejoramos Problemas en lineas rectas que salgan de zona incluyendo limite con circunferencia de region de salida
	- Proxima version con inclusion de poo con ficheros separados

V7  15/05/21

	- Separacion de objetos usados para generalización de aplicación
	- Mejoras en GUI. Implementación de nuebos botones
	- Problemas con las restricciones y cambio de dirección

V8 26/05/2021

	- Cambios en cinemática inversa con simplificación
	- Generalizacion de atributos en libreria Movement_calc
	- Mejora de rendimiento de vizualización en CoppeliaSim

V9 26/06/2021
	- Incluimos Socket library
	- Cambio de funciones en Api y Robot para Implementación
	- Nuevas funciones en Movement_calc

V10 _ CoppeliTest 15/07/2021
	- Integracion de Coppelia sim con nueva interfaz y funcionamiento sincronizado
	- Elección de simulador con coppelia o con robot
	- Pruebas de Cinematica Inversa con Coppelia sim y nueva lógica
	- Abstracción de la conexión mediante connectionObjtc. De esta forma podemos trabajar con una sola clase
	para cualquier caso de funcionamiento.

V11 15/08/2021	
	- Nueva interfaz visual
	- Inclusion de modificaciones personalizada mediante barra de menu
	- Creacion de cichero DataFile donde se guardarán los valores generales de funcionamiento para una 
	experiencia más fluida
	- Inclusion de opcion debug para poder hacer pruebas sin necesidad de conexión

V12 20/09/2021
	- cambio de comandos a enviar
	- optimización de threads the recepción y emisión. Planteamiento the puerto virtual entre arduino y cliente
	- Visualización en tiempo real de posiciones de cada motor

V3 15/10/2021
	- Prueb nueva paquetización
	- Estructuración de código
	- Optimizacion de funciones no usadas
	- Funcionslidad principal establecida
	- Interfaz visual completa
	- Inclusion de opciones TCP/UDP para conexión
	- Mayor manejo de información del robot