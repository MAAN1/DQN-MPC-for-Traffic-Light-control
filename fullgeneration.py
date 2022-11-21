import numpy as np


class fullTrafficGenerator:

    def routes(self, seed):

        np.random.seed(seed)

        self.Low1 = np.random.poisson(0.13, 720)
        self.Low2 = np.random.poisson(0.086, 720)
        self.Low3 = np.random.poisson(0.086, 720)
        self.Low4 = np.random.poisson(0.05, 720)
        self.Low5 = np.random.poisson(0.2, 720)

        self.Med1 = np.random.poisson(0.52, 720)
        self.Med2 = np.random.poisson(0.35, 720)
        self.Med3 = np.random.poisson(0.35, 720)
        self.Med4 = np.random.poisson(0.2, 720)
        self.Med5 = np.random.poisson(0.8, 720)

        self.Hig1 = np.random.poisson(0.975, 720)
        self.Hig2 = np.random.poisson(0.645, 720)
        self.Hig3 = np.random.poisson(0.645, 720)
        self.Hig4 = np.random.poisson(0.375, 720)
        self.Hig5 = np.random.poisson(1.5, 720)

        self.lane_1 = sum(self.Low1) + sum(self.Med1) + sum(self.Hig1)
        self.lane_2 = sum(self.Low2) + sum(self.Med2) + sum(self.Hig2)
        self.lane_3 = sum(self.Low3) + sum(self.Med3) + sum(self.Hig3)
        self.lane_4 = sum(self.Low4) + sum(self.Med4) + sum(self.Hig4)
        self.lane_5 = sum(self.Low5) + sum(self.Med5) + sum(self.Hig5)
        self.total_num_vehic = self.lane_1 + self.lane_2 + self.lane_3 + self.lane_4 + self.lane_5




        self.Low = np.add(self.Low1, self.Low2)
        self.Low = np.add(self.Low, self.Low3)
        self.Low = np.add(self.Low, self.Low4)
        self.Low = np.add(self.Low, self.Low5)


        self.Med = np.add(self.Med1, self.Med2)
        self.Med = np.add(self.Med, self.Med3)
        self.Med = np.add(self.Med, self.Med4)
        self.Med = np.add(self.Med, self.Med5)


        self.Hig = np.add(self.Hig1, self.Hig2)
        self.Hig = np.add(self.Hig, self.Hig3)
        self.Hig = np.add(self.Hig, self.Hig4)
        self.Hig = np.add(self.Hig, self.Hig5)

        self.Traffic_Arrival = np.concatenate((self.Low, self.Med, self.Hig))

        with open("incrocio.rou.xml", "w") as routes:
            print("""<routes>
                <vType id="typeE2TL1" accel="2.6" decel="4.5"  length="4.0" minGap="2" maxSpeed="50" sigma="0.5" />
                <vType id="typeN2TL2" accel="2.6" decel="4.5"  length="4.0" minGap="2" maxSpeed="50" sigma="0.5" />
                <vType id="typeN2TL3" accel="2.6" decel="4.5"  length="4.0" minGap="2" maxSpeed="50" sigma="0.5" />
                <vType id="typeW2TL4" accel="2.6" decel="4.5"  length="4.0" minGap="2" maxSpeed="50" sigma="0.5" />
                <vType id="typeW2TL5" accel="2.6" decel="4.5"  length="4.0" minGap="2" maxSpeed="50" sigma="0.5" />

                <route id = "E2TL1" edges = "E2TL1 E17 E18 E10"/>
                <route id = "N2TL2" edges = "N2TL23 E7 E12"/>
                <route id = "N2TL3" edges = "N2TL23 E8 E10"/>
                <route id = "W2TL4" edges = "W2TL45 E11 E19 E20 E22"/>
                <route id = "W2TL5" edges = "W2TL45 E11 E12"/>
                """, file=routes)

            veh_num = 0
            indexl = 0

            for i in range(0, 3600, 5):
                vehLow1 = self.Low1[indexl]

                while vehLow1 > 0:
                    print(' <vehicle id = "E2TL1_%i" type = "typeE2TL1" route = "E2TL1" depart = "%i" />' % (veh_num, i),
                          file=routes)
                    veh_num += 1
                    vehLow1 -= 1

                vehLow2 = self.Low2[indexl]
                while vehLow2 > 0:
                    print(' <vehicle id = "N2TL2_%i" type = "typeN2TL2" route = "N2TL2" depart = "%i" />' % (veh_num, i),
                          file=routes)
                    veh_num += 1
                    vehLow2 -= 1

                vehLow3 = self.Low3[indexl]
                while vehLow3 > 0:
                    print(' <vehicle id = "N2TL3_%i" type = "typeN2TL3" route = "N2TL3" depart = "%i" />' % (veh_num, i),
                          file=routes)
                    veh_num += 1
                    vehLow3 -= 1

                vehLow4 = self.Low4[indexl]
                while vehLow4 > 0:
                    print(' <vehicle id = "W2TL4_%i" type = "typeW2TL4" route = "W2TL4" depart = "%i" />' % (veh_num, i),
                      file=routes)
                    veh_num += 1
                    vehLow4 -= 1

                vehLow5 = self.Low5[indexl]
                while vehLow5 > 0:
                    print(' <vehicle id = "W2TL5_%i" type = "typeW2TL5" route = "W2TL5" depart = "%i" />' % (veh_num, i),
                      file=routes)
                    veh_num += 1
                    vehLow5 -= 1
                indexl += 1

            indexm = 0
            for j in range(3600, 7200, 5):
                vehMed1 = self.Med1[indexm]

                while vehMed1 > 0:
                    print(
                        ' <vehicle id = "E2TL1_%i" type = "typeE2TL1" route = "E2TL1" depart = "%i" />' % (veh_num, j),
                        file=routes)
                    veh_num += 1
                    vehMed1 -= 1

                vehMed2 = self.Med2[indexm]
                while vehMed2 > 0:
                    print(
                        ' <vehicle id = "N2TL2_%i" type = "typeN2TL2" route = "N2TL2" depart = "%i" />' % (veh_num, j),
                        file=routes)
                    veh_num += 1
                    vehMed2 -= 1

                vehMed3 = self.Med3[indexm]
                while vehMed3 > 0:
                    print(
                        ' <vehicle id = "N2TL3_%i" type = "typeN2TL3" route = "N2TL3" depart = "%i" />' % (veh_num, j),
                        file=routes)
                    veh_num += 1
                    vehMed3 -= 1

                vehMed4 = self.Med4[indexm]
                while vehMed4 > 0:
                    print(
                        ' <vehicle id = "W2TL4_%i" type = "typeW2TL4" route = "W2TL4" depart = "%i" />' % (veh_num, j),
                        file=routes)
                    veh_num += 1
                    vehMed4 -= 1

                vehMed5 = self.Med5[indexm]
                while vehMed5 > 0:
                    print(
                        ' <vehicle id = "W2TL5_%i" type = "typeW2TL5" route = "W2TL5" depart = "%i" />' % (veh_num, j),
                        file=routes)
                    veh_num += 1
                    vehMed5 -= 1
                indexm += 1

            indexh = 0
            for t in range(7200, 10800, 5):
                vehHig1 = self.Hig1[indexh]

                while vehHig1 > 0:
                    print(
                        ' <vehicle id = "E2TL1_%i" type = "typeE2TL1" route = "E2TL1" depart = "%i" />' % (veh_num, t),
                        file=routes)
                    veh_num += 1
                    vehHig1 -= 1

                vehHig2 = self.Hig2[indexh]
                while vehHig2 > 0:
                    print(
                        ' <vehicle id = "N2TL2_%i" type = "typeN2TL2" route = "N2TL2" depart = "%i" />' % (veh_num, t),
                        file=routes)
                    veh_num += 1
                    vehHig2 -= 1

                vehHig3 = self.Hig3[indexh]
                while vehHig3 > 0:
                    print(
                        ' <vehicle id = "N2TL3_%i" type = "typeN2TL3" route = "N2TL3" depart = "%i" />' % (veh_num, t),
                        file=routes)
                    veh_num += 1
                    vehHig3 -= 1

                vehHig4 = self.Hig4[indexh]
                while vehHig4 > 0:
                    print(
                        ' <vehicle id = "W2TL4_%i" type = "typeW2TL4" route = "W2TL4" depart = "%i" />' % (veh_num, t),
                        file=routes)
                    veh_num += 1
                    vehHig4 -= 1

                vehHig5 = self.Hig5[indexh]
                while vehHig5 > 0:
                    print(
                        ' <vehicle id = "W2TL5_%i" type = "typeW2TL5" route = "W2TL5" depart = "%i" />' % (veh_num, t),
                        file=routes)
                    veh_num += 1
                    vehHig5 -= 1
                indexh += 1

            print("</routes>", file=routes)