#!/usr/bin/python3
import re, io, glob, sys, logging
from datetime import datetime
from pathlib import Path
from collections import Counter
from multiprocessing import Pool
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

logging.basicConfig(level=logging.WARNING)

ES_PORT = 9200

ES_INDEX_PUBLI = 'publication'
MAPPING_PUBLI = {
	"settings": {
		"number_of_shards": 1,
		"index": {
			"analysis": {
				"analyzer": {
					"synonym": {
						"tokenizer": "whitespace",
						"filter": [ "synonym" ]
					}
				},
				"filter": { 
					"synonym" : {
					    "type" : "synonym",
					    "synonyms" : [
							"AAAE => African Association of Agricultural Economists",
							"AACB => Association of African Central Banks",
							"AAEA => Agricultural and Applied Economics Association",
							"AAEE => Austrian Association for Energy Economics",
							"AARES => Australian Agricultural and Resource Economics Society",
							"AAYE => Association of African Young Economists",
							"ABEF => Association of Behavioral Economics and Finance",
							"ABF => Association for Banking and Finance",
							"ABF => American Bar Foundation",
							"ABH => Association of Business Historians",
							"ACAES => American Committee on Asian Economic Studies",
							"ACCF => American Council for Capital Formation",
							"ACE => Association of Caribbean Economists",
							"ACE => Association of Christian Economists",
							"ACE => Association of Competition Economics",
							"ACE => UK Association of Christian Economists",
							"ACE => Aboa Centre for Economics",
							"ACED => Agency for Cooperation, Education and Development",
							"ACEI => Association for Cultural Economics International",
							"ACEP => Africa Center for Energy Policy",
							"ACERH => Australian Centre for Economic Research on Health",
							"ACES => Association for Comparative Economic Studies",
							"ACET => African Center for Economic Transformation",
							"ACFEA => Asian Consumer and Family Economics Association",
							"ACIAR => Australian Centre for International Agricultural Research",
							"ACIT => Academic Consortium on International Trade",
							"ADE => Association for Documentation in Economics",
							"ADRI => Asian Development Research Institute",
							"AEA => American Economic Association",
							"AEA => Armenian Economic Association",
							"AEAG => Agricultural Economics Association of Georgia",
							"AEASA => Agricultural Economics Association of South Africa",
							"AEF => Academy of Economics and Finance",
							"AEFP => Association for Education Finance and Policy",
							"AEHN => African Economic History Network",
							"AERA => Agricultural Economics Research Association (India)",
							"AES => African Econometric Society",
							"AES => Agricultural Economics Society",
							"AESA => Association for Economic and Social Analysis",
							"AESS => Asian Economic and Social Society",
							"AFA => African Finance Association",
							"AFA => American Finance Association",
							"AFA => Asian Finance Association",
							"AFAANZ => Accounting and Finance Association of Australia and New Zealand",
							"AFBM => Australasian Farm Business Management Network",
							"AFDIE => Association Française pour le Développement de l'Intelligence Économique",
							"AFEA => African Finance and Economics Association",
							"AFEE => Association for Evolutionary Economics",
							"AFESD => Arab Fund for Econimic and Social Development",
							"AFI => Grupo Analistas",
							"AFMA => African Farm Management Association",
							"AFRA => Accounting and Finance Research Association",
							"AFS => Asian Financial Society",
							"AGE => Association of Gulf Economists",
							"AHE => Association for Heterodox Economics",
							"AHES => Australian Health Economics Society",
							"AHWI => Australian Health Workforce Institute",
							"AIAE => African Institute for Applied Economics",
							"AIEA2 => Association Internationale d'Economie Alimentaire et Agroindustrielle",
							"AIEFS => Association of Indian Economic and Financial Studies",
							"AIFE => American Institute for Full Employment",
							"AIFFA => Africa Institute for Forecasting and Financial Analysis",
							"AIID => Amsterdam Institute for International Development",
							"AIPRG => Armenian International Policy Research Group",
							"AIRLEAP => Association for Integrity and Responsible Leadership in Economics and Associated Professions",
							"AIT => Austrian Institute of Technology",
							"AIUB => American International University-Bangladesh",
							"ALBA => Athens Laboratory of Business Administration",
							"ALCEE => Alabama Council on Economic Education",
							"ALEA => American Law and Economics Association",
							"AMF => Arab Monetary Fund",
							"AMFET => Association for Modelling and Forecasting Economies in Transition",
							"AMRO => ASEAN+3 Macroeconomic Research Office",
							"AMS => Australasian Macroeconomics Society",
							"APDU => Association of Public Data Users",
							"APEC => Asia-Pacific Economic Cooperation",
							"APEC => Atlantic Provinces Economic Council",
							"APEE => Association of Private Enterprise Education",
							"APET => Association for Public Economic Theory",
							"APF => Athenian Policy Forum",
							"APF => Athenian Policy Forum",
							"API => Arab Planning Institute",
							"APPAM => Association for Public Policy Analysis and Management",
							"APRNet => Agricultural Policy Research Network",
							"ARARI => Amhara Regional Agricultural Research Institute",
							"AREA => American Rehabilitation Economics Association",
							"ARES => American Real Estate Society",
							"ARES => Association for Real Estate Securitization",
							"ARETT => Association of Independent Centers of Economic Analysis",
							"AREU => Afghanistan Research and Evaluation Unit",
							"AREUEA => American Real Estate and Urban Economics Association",
							"ARIA => American Risk and Insurance Association",
							"ARSC => Applied Regional Science Council",
							"ASA,B&E => American Statistical Association, Business and Economic Statistics Section",
							"ASE => Association for Social Economics",
							"ASEAN => Association of Southeast Asian Nations",
							"ASGE => Association for the Study of the Grants Economy",
							"ASHE => American Society of Hispanic Economists",
							"ASLEA => Asian Law and Economics Association",
							"ASMECI => Association marocaine d'études et de recherches en économie islamique",
							"ASPE => Association for Studies in Public Economics",
							"ASREC => Association for the Study of Religion, Economics, and Culture",
							"ASSET => Association of Southern European Economic Theorists",
							"ASUE => Armenian State University of Economics",
							"ATHEA => Austrian Health Economics Association",
							"ATINER => Athens Institute for Education and Research",
							"AUBER => Association for University Business and Economic Research",
							"AUEB => Athens University of Economics and Business",
							"AWEPON => African Women's Economic Policy Network",
							"Akroasis => Scientific Society for the Promotion and Advancement of Social Sciences",
							"AustLEA => Australian Law and Economics Association",
							"BAIPHIL => Bankers Institute of the Philippines",
							"BALAS => Business Association of Latin American Studies",
							"BDPEMS => Berlin Doctoral Program of Economics and Management Science",
							"BFAP => Bureau for Food and Agricultural Policy",
							"BFS => Bachelier Finance Society",
							"BIEE => British Institute of Energy Economics",
							"BIEF => Baltic Institute of Economy and Finance",
							"BIISS => Bangladesh Institute of International and Strategic Studies",
							"BIRD => Bankers Institute of Rural Development",
							"BIS => Bank for International Settlements",
							"BITS => Birla Institute of Technology and Science",
							"BITS => Business and Information Technology School",
							"BPATC => Bangladesh Public Administration Training Centre",
							"BRDC => Bangladesh Development Research Center",
							"BUBT => Bangladesh University of Business and Technology",
							"CABE => Canadian Association for Business Economics",
							"CAES => Caribbean Agro-Economic Society",
							"CAIRN => Canadian Agricultural Innovation and Regulation Network",
							"CANSEE => Canadian Society for Ecological Economics",
							"CASSE => Center for the Advancement of the Steady State Economy",
							"CATPRN => Canadian Agricultural Trade Policy Research Network",
							"CBGA => Centre for Budget and Governance Accountability",
							"CCEHPE => Chicago Center of Excellence in Health Promotion Economics",
							"CCMF => Caribbean Centre for Money and Finance",
							"CCS => Chaudhary Charan Singh Haryana Agricultural University",
							"CDDEP => Center for Disease Dynamics, Economics and Policy",
							"CDESG => Canadian Development Economics Study Group",
							"CDRI => Cambodia Development Resource Institute",
							"CEA => Canadian Economics Association",
							"CEANA => Chinese Economic Association in North America",
							"CEAUK => Chinese Economic Association (UK)",
							"CEBERG => Canadian Experimental & Behavioral Economics Research Group",
							"CEBRA => Central Bank Research Association",
							"CEDA => Committee for Economic Development of Australia",
							"CEEC => European Council of Construction Economists",
							"CEEP => European Consortium on Landscape Economics",
							"CEFIG => Center for Firms in the Global Economy",
							"CEMMAP => Centre for Microdata Methods and Practice",
							"CEPA => Centre for Policy Analysis",
							"CEPA => Centre for Poverty Analysis",
							"CEPR => Center for Economic and Policy Research",
							"CERIK => Construction and Economy Research Institute of Korea",
							"CERISE => Centre for Russian International Socio-political and Economic Studies",
							"CES => Cyprus Economic Society",
							"CESAA => Contemporary European Studies Association of Australia",
							"CESG => Canadian Econometric Study Group",
							"CESRAN => Centre for Strategic Research and Analysis",
							"CESS => Centre for Economic and Social Studies",
							"CFE => Korea Center for Free Enterprise",
							"CGA => Certified General Accountants Association of Canada",
							"CGIAR => Consultative Group on International Agricultural Research",
							"CHILD => Centre for Household, Income, Labour and Demographic Economics",
							"CIDEF => Chartered Institute of Development Finance",
							"CIEM => Central Institution for Economic Management",
							"CIESR => Caucasian Institute for Economic and Social Research",
							"CIFAR => Canadian Institute for Advanced Research",
							"CIIM => Cyprus International Institute of Management",
							"CIMP => Chandragupt Institute of Management Patna",
							"CIRET => Centre for International Research on Economic Tendency Surveys",
							"CKF => Center for Economic Forecasting of Mexico",
							"CLBC => Canadian Labour and Business Centre",
							"CMDR => Centre for Multi-disciplinary Development Research",
							"CNAC => CNA Corporation",
							"CNEH => Canadian Network for Economic History",
							"CNP => Center for National Policy",
							"COMESA => Common Market for Eastern and Southern Africa",
							"COPE => Congress Of Political Economists",
							"CPD => Centre for Policy Dialogue",
							"CPEG => Canadian Public Economics Study Group",
							"CPR => Centre for Policy Research",
							"CPRN => Canadian Policy Research Networks",
							"CPRSPD => Centre for Poverty Reduction and Social Policy Development",
							"CRCE => Centre for Research into Post-Communist Economies",
							"CREC => Center for Regional Economic Competitiveness",
							"CREE => Canadian Resource and Environmental Economics Study Group",
							"CREEA => Canadian Resource and Environmental Economics Association",
							"CREMA => Center for Research in Economics, Management and the Arts",
							"CREST => Centre for Research on Economic and Social Transformation",
							"CRIW => Conference on Research in Income and Wealth",
							"CRSA => Canadian Regional Science Association",
							"CSEA => Center for the Study of the Economies of Africa",
							"CSH => Centre de Sciences Humaines",
							"CSHET => China Society for the History of Economic Thought",
							"CSIL => Centre for Industrial Studies",
							"CSIRD => Centre for Studies in International Relations and Development",
							"CSIRO => Commonwealth Scientific and Industrial Research Organisation",
							"CSLS => Center for the Study of Living Standards",
							"CSPET => Chinese Society for the Promotion of Economic Theory",
							"CSPS => Centre for Strategic and Policy Studies",
							"CSS => Centre for Social Studies",
							"CSWE => China Society of World Economics",
							"CUFE => Central University of Finance and Economics",
							"CUNY => City University of New York",
							"CURISES => Curacao Institute for Social and Economic Studies",
							"CWAE => Committee on Women in Agricultural Economics",
							"CWE => Chinese Women Economists",
							"CWEN => Canadian Women Economists Network",
							"Cheiron => International Society for the History of Behavioral and Social Sciences",
							"DES => Dansk Energiøkonomisk Selskab",
							"DIW => German Institute for Economic Research",
							"DPI => Development Planning Institute",
							"EAAE => European Association of Agricultural Economists",
							"EABER => East Asian Bureau of Economic Research",
							"EABH => European Association for Banking and Financial History E. V.",
							"EADI => European Association of Development Research and Training Institutes",
							"EAE => European Association of Economists",
							"EAEA => East Asian Economic Association",
							"EAEFEASA => European-Asian Economics, Finance, Econometrics and Accounting Science Association",
							"EAEPE => European Association for Evolutionary Political Economy",
							"EAERE => European Association of Environmental and Resource Economists",
							"EAFE => European Association of Fisheries Economists",
							"EALE => European Association of Law and Economics",
							"EARIE => European Association for Research in Industrial Economics",
							"EBEA => Economics and Business Education Association",
							"EBHS => Economic and Business Historical Society",
							"EBRD => European Bank for Reconstruction and Development",
							"EBS => European Business School",
							"ECDPM => European Centre for Development Policy Management",
							"ECGI => European Corporate Governance Institute",
							"ECHE => European Conference on the History of Economics",
							"ECINEQ => Society for the Study of Economic Inequality",
							"ECIPE => European Centre for International Political Economy",
							"ECMI => European Capital Markets Institute",
							"ECOWAS => Economic Community of West African States",
							"ECRI => Economic Cycle Research Institute",
							"EDAC => Economic Developers Association of Canada",
							"EDF => Environmental Defense Fund",
							"EDII => Entrepreneurship Development Institute of India",
							"EDINEB => EDucational INnovation in Economics and Business Network",
							"EEA => Eastern Economic Association",
							"EEA => Ethiopian Economic Association",
							"EEPRI => Ethiopian Economic Policy Research Institute",
							"EFA => Eastern Finance Association",
							"EGRG => Royal Geographical Society, Economic Geography Research Group",
							"EHESS => École des Hautes Études en Sciences Sociales",
							"EHS => Economic History Society",
							"EHSANZ => Economic History Society of Australia and New Zealand",
							"EHSSA => Economic History Society of Southern Africa",
							"EIDE => European Institute for Development and Education",
							"EIEE => RFF-CMCC European Institute on Economics and the Environment",
							"EIF => European Investment Fund",
							"EIILM => Eastern Institute for Integrated Learning in Management",
							"EIPA => European Institute of Public Administration",
							"EMS => European Management School",
							"ENARPRI => European Network of Agricultural and Rural Policy Research Institutes",
							"ENEPRI => European Network of Economic Policy Research Institutes",
							"ENER => European Network on the Economics of Religion",
							"ENSA => Economics of National Security Association",
							"EPCS => European Public Choice Society",
							"EPIP => European Policy for Intellectual Property",
							"EPRC => Economic Policy Research Centre",
							"EPS => Economists for Peace and Security",
							"ER => Associazione-Fondazione EconomiaReale",
							"ERA => Econometric Research Association",
							"ERES => European Real Estate Society",
							"ERF => Economic Research Forum",
							"ERI => Economic Research Institute",
							"ERI => Enterprise Research Institute",
							"ERIA => Economic Research Institute for ASEAN and East Asia",
							"ERINA => Economic Research Institute for Northeast Asia",
							"ESA => Economic Science Association",
							"ESCE => Economic and Social Research Center",
							"ESHIA => Society for Economic Science with Heterogeneous Interacting Agents",
							"ESHSI => Economic and Social History Society of Ireland",
							"ESMT => European School of Management and Technology",
							"ESRF => Economics and Social Research Foundation",
							"ESRI => Economic and Social Research Institute",
							"ETC => Entrepreneuship Training Center",
							"EUDN => European Development Research Network",
							"EUHEA => European Association of Health Economics",
							"EUNIP => European Network on Industrial Policy",
							"EURADA => European Association of Development Agencies",
							"EUROFRAME => European Forecasting Research Association for the Macro-Economy",
							"EXCAS => European Xtramile Centre of African Studies",
							"FAERE => French Association of Environmental and Resource Economists",
							"FDRS => Food Distribution Research Society",
							"FEA => Financial Education Association",
							"FECAP => Facultade de Economia e Comércio Álvares Penteado",
							"FEED => Foundation for European Economic Development",
							"FEPS => Foundation for European Progressive Studies",
							"FIRS => Financial Intermediation Research Society",
							"FITA => Federation of International Trade Associations",
							"FPA => Financial Planning Association",
							"FREIT => Forum for Research in Empirical International Trade",
							"FTE => Foundation for Teaching Economics",
							"GAEE => Global Association of Economics Education",
							"GALE => Greek Association of Law and Economics",
							"GAPE => Greek Scientific Association of Political Economy",
							"GARP => Global Association of Risk Professionals",
							"GCF => Global Commerce Forum",
							"GDN => Global Development Network",
							"GDRC => Global Development Research Center",
							"GEM-IWG => Gender and Macro International Working Group",
							"GEM-IWG => International Working Group on Gender, Macroeconomics and International Economics",
							"GERA => Global Entrepreneurship Research Association",
							"GESY => Sonderforschungsbereich/Transregio 15 Governance and the Efficiency of Economic Systems",
							"GFA => Global Finance Association",
							"GIGA => German Institute of Global and Area Studies",
							"GIMPA => Ghana Institute of Management and Public Administration",
							"GIPA => Georgian Institute of Public Affairs",
							"GKEC => Global Knowledge Economics Council",
							"GRIPS => National Graduate Institute for Policy Studies",
							"GSEFM => Graduate School of Economics, Finance and Management",
							"GSSI => Gran Sasso Science Institute",
							"GTS => Game Theory Society",
							"Globelics => Global Network for Economics of Learning, Innovation, and Competence Building Systems",
							"HEAI => Health Economics Association of India",
							"HEAI => Health Economics Association of Ireland",
							"HECER => Helsinki Center for Economic Research",
							"HESG => Health Economists' Study Group",
							"HESPI => Horn Economic and Social Policy Institute",
							"HKUST => Hong Kong University of Science and Technology",
							"HSBA => Hamburg School of Business Administration",
							"HSRC => Human Sciences Research Council",
							"HWWI => Hamburg Institute of International Economics",
							"I-SIE => Islamic Society of Institutional Economics",
							"IAAE => International Association for Applied Econometrics",
							"IAAE => International Association of Agricultural Economists",
							"IAAEM => International Association of Aquaculture Economics and Management",
							"IACMR => International Association for Chinese Management Research",
							"IAEE => International Association for Energy Economics",
							"IAEFL => International Academy of Economics, Finance and Law",
							"IAES => International Atlantic Economic Society",
							"IAES => Iranian Agricultural Economics Society",
							"IAFA => Irish Accounting and Finance Association",
							"IAFEP => International Association for the Economics of Participation",
							"IAFFE => International Association for Feminist Economics",
							"IAHPR => International Academy of Health Preference Research",
							"IAME => International Association of Maritime Economists",
							"IAOS => International Association for Official Statistics",
							"IAPRI => Indaba Agricultural Policy Research Institute",
							"IAREP => International Association for Research in Economic Psychology",
							"IARI => Indian Agricultural Research Istitute",
							"IARIW => International Association for Research in Income and Wealth",
							"IASC => International Association for the Study of the Commons",
							"IASRI => Indian Agricultural Statistics Research Institute",
							"IATE => International Association for Tourism Economics",
							"IBEC => International Bank for Economic Co-operation",
							"IBEFA => International Banking, Economics and Finance Association",
							"ICAPE => International Confederation of Associations for Pluralism in Economics",
							"ICEG => International Center for Economic Growth",
							"ICEN => Institute of Chartered Economists of Nigeria",
							"ICER => Institute for Clinical and Economic Review",
							"ICER => International Centre for Economic Research",
							"ICLE => International Center for Law and Economics",
							"ICMB => International Center for Monetary and Banking Studies",
							"ICRIER => Indian Council for Research on International Economic Relations",
							"ICSTAT => International Cooperation Center for Statistics 'Luigi Bodio'",
							"ICTSD => International Centre for Trade and Sustainable Development",
							"IDC => Interdisciplinary Center",
							"IDEAS => Institute of Development and Economic Alternatives",
							"IDRC => International Development Research Center",
							"IEA => Indian Economic Association",
							"IEA => International Economic Association",
							"IEA => Iranian Economic Association",
							"IEA => Irish Economic Association",
							"IEA => Institute of Economic Affairs",
							"IEA => International Energy Agency",
							"IEDC => International Economic Development Council",
							"IEML => Institute of Economics, Management and Law",
							"IEWRI => International Economy & Work Research Institute",
							"IFA => Indonesian Finance Association",
							"IFAMA => International Food and Agribusiness Management Association",
							"IFMR => Institute for Financial Management Research",
							"IFPRI => International Food Policy Research Institute",
							"IFREE => International Foundation for Research in Experimental Economics",
							"IFS => Institute for Fiscal Studies",
							"IGC => International Growth Centre",
							"IGES => Institute for Global Environmental Strategies",
							"IHD => Institute for Human Development",
							"IIASA => International Institute for Applied Systems Analysis",
							"IIDS => Indian Institute of Dalit Studies",
							"IIE => Peter G. Peterson Institute for International Economics",
							"IIEA => International Indian Economists Association",
							"IIEA => International Iranian Economic Association",
							"IIFET => International Institute of Fisheries Economics and Trade",
							"IIFT => Indian Institute of Foreign Trade",
							"IIHEM => International Institute for Higher Education in Morocco",
							"IIM => International Institute of Management",
							"IIMA => Indian Institute of Management Ahmedabad",
							"IIMB => Indian Institute of Management Bangalore",
							"IIMCAL => Indian Institute of Management Calcutta",
							"IIME => Institute of Innovative Management of the Economy",
							"IIMIDR => Indian Institute of Management Indore",
							"IIML => Indian Institute of Management Lucknow",
							"IIOA => International Input-Output Association",
							"IIPM => Indian Institute of Planning and Management",
							"IIPS => Institute for International Policy Studies",
							"IISE => Institute for International Socio-Economic Studies",
							"IISEPS => Independent Institute of Socio-Economic & Political Studies",
							"IISRE => International Institute for Sustainable Regional Economies",
							"IISWBM => Indian Institute of Social Welfare and Business Management",
							"IIUM => International Islamic University Malaysia",
							"ILCUK => International Longevity Centre-UK",
							"ILEA => Israeli Association for Law and Economics",
							"ILPF => Institute of Local Public Finance",
							"IMA => International Microsimulation Association",
							"IMD => International Institute for Management",
							"IME => Inframarginal Economics Society",
							"IME => Institute for Market Economics",
							"IMEHA => International Maritime Economic History Association",
							"IMF => International Monetary Fund",
							"IMI => International Management Institute",
							"IMPS => Institute for Management and Planning Studies",
							"INAHEA => Indonesian Health Economics Association",
							"INC => Innovations and Consulting Centre",
							"INCEIF => International Centre for Education in Islamic Finance",
							"INDEF => Institute for Development of Economics and Finance",
							"INED => International Network for Economic Developers",
							"INFORMS => Institute for Operations Research and the Management Sciences",
							"INILAK => Independent Institute of Lay Adventists of Kigali",
							"INSEE => Indian Society for Ecological Economics",
							"INSIDE => Insight on Immigration and Development Economics",
							"IOBE => Foundation for Economic and Industrial Research",
							"IOS => Industrial Organization Society",
							"IOSCO => International Organisation of Securities Commissions",
							"IPA => Innovations for Poverty Action",
							"IPAR => Institute for Policy Analysis and Research",
							"IPEG => Barcelona Institute for Political Economy and Governance",
							"IPM => Institute for Privatization and Management",
							"IPPM => Institute of Public Policy Management",
							"IPS => Institute of Policy Studies",
							"IRAEE => Iranian Association for Energy Economics",
							"IRES => International Real Estate Society",
							"IRMA => Institute of Rural Management",
							"ISAE => Indian Society of Agricultural Economics",
							"ISBA => International Society for Bayesian Analysis",
							"ISBEE => International Society of Business, Economics and Ethics",
							"ISCR => New Zealand Institute for the Study of Competition and Regulation",
							"ISE => Israel Society for Economics",
							"ISEC => Institute for Social and Economic Change",
							"ISED => Institute of Small Enterprises and Development",
							"ISI => International Statistical Institute",
							"ISID => Institute for Studies in Industrial Development",
							"ISINI => International Society for Intercommunication of New Ideas",
							"ISIR => International Society for Inventory Research",
							"ISM => International School of Management",
							"ISNE => Irish Society of New Economists",
							"ISPOR => International Society for Pharmacoeconomics and Outcomes Research",
							"ISQOLS => International Society for Quality-of-Life Studies",
							"ISS => International Joseph A. Schumpeter Society",
							"ISS => Institute of Social Studies",
							"ISSBS => International School for Social and Business Studies",
							"ISSER => Institute of Statistical, Social and Economic Research",
							"IT&FA => International Trade and Finance Association",
							"ITIF => Information Technology and Innovation Foundation",
							"IUE => International Union of Economists",
							"IUPUI => Indiana University-Purdue University",
							"IWGVT => International Working Group on Value Theory",
							"IWMI => International Water Management Institute",
							"JACES => Japan Association for Comparative Economic Studies",
							"JAEG => Japan Association of Economic Geographers",
							"JAFEE => Japan Association for Evolutionary Economics",
							"JASESS => Japan Association for Social and Economic Systems Studies",
							"JASID => Japan Society for International Development",
							"JBIMS => Jamnalal Bajaj Institute of Management Studies",
							"JCER => Japan Center for Economic Research",
							"JEA => Japanese Economic Association",
							"JILAEE => Joint Initiative for Latin American Experimental Economics",
							"JIMS => Jerusalem Institute for Market Studies",
							"JPRI => Japan Policy Research Institute",
							"JSCES => Japanese Society for Comparative Economic Studies",
							"JSHET => Japanese Society for The History of Economic Thought",
							"JSME => Japan Society of Monetary Economics",
							"JSPE => Japan Society of Political Economy",
							"JSPEHHC => Japanese Society for the Polical Economy of Health and Health Care",
							"JSPKE => Japanese Society for Post Keynesian Economics",
							"KACE => Korea Association of Cultural Economics",
							"KAEA => Korea Agricultural Economics Association",
							"KAFA => Korea-America Finance Association",
							"KAIST => Korea Advanced Institute of Science and Technology",
							"KALS => Korean Association of Labor Studies",
							"KAPAE => Korea Association for Policy Analysis and Evaluation",
							"KAPFE => Korean Association of Public Finance and Economics",
							"KASBIT => Khadim Ali Shah Bukhari Institute of Technology",
							"KASIO => Korea Academic Society of Industrial Organization",
							"KATIS => Korean Association of Trade and Industry Studies",
							"KDEA => Korea Development Economics Association",
							"KDGW => Koreanisch-Deutsche Gesellschaft für Wirthschaftswissenschaften",
							"KDI => Korea Development Institute",
							"KDIC => Korea Deposit Insurance Corporation",
							"KEA => Kentucky Economic Association",
							"KEA => Korean Economics Association",
							"KEBA => Korea Economics and Business Association",
							"KEEA => Korean Environmental Economics Association",
							"KEI => Korea Economic Institute",
							"KEPE => Centre for Planning and Economic Research",
							"KERC => Kyushu Economic Research Center",
							"KERI => Korea Economic Research Institute",
							"KES => Korean Econometric Society",
							"KFIRI => Korea Fixed Income Research Institute",
							"KFMA => Korean Financial Management Association",
							"KIEP => Korea Institute for International Economic Policy",
							"KIET => Korea Institute for Industrial Economics and Trade",
							"KILF => Korea Institute of Local Finance",
							"KIPF => Korea Institute of Public Finance",
							"KIPPRA => Kenya Institute for Public Policy Research and Analysis",
							"KIRI => Korea Insurance Research Institute",
							"KISDI => Korea Information Society Development Institute",
							"KIST => Korea Institute of Science and Technology",
							"KJEM => The Korean-Japanese Economics & Management Association",
							"KLEA => Korean Law and Economics Association",
							"KLI => Korea Labor Institute",
							"KMFA => Korea Money and Finance Association",
							"KNUST => Kwame Nkrumah University of Science and Technology",
							"KREI => Korea Rural Economic Institute",
							"KRIHS => Korea Research Institute for Human Settlements",
							"KRILA => Korea Research Institution for Local Administration",
							"KRSA => Korean Regional Science Association",
							"KSESA => Korean Social and Economic Studies Association",
							"KSRI => Korea Security Research Institute",
							"LACEEP => Latin American and Caribbean Environmental Economics Program",
							"LAI => Lambda Alpha International",
							"LARES => Latin American Real Estate Association",
							"LBS => London Business School",
							"LBSIM => Lal Bahadur Shastri Institute of Management",
							"LEA => Lebanese Economic Association",
							"LEANZ => Law and Economics Association of New Zealand",
							"LFMI => Lithuanian Free Market Institute",
							"LGERI => LG Economic Research Institute",
							"LIDC => London International Development Centre",
							"LIS => Luxembourg Income Study",
							"LRSP => Laboratory for Research in Statistics and Probability",
							"LSE => London School of Economics",
							"MAEA => Malaysian Agricultural Economics Association",
							"MAER => Meta-Analysis of Economic Research Network",
							"MEA => Midwest Economics Association",
							"MEA => Minnesota Economics Association",
							"MEEA => Middle East Economic Association",
							"MEG => Midwest Econometrics Group",
							"MEPC => Mississippi Economic Policy Center",
							"MERI => Mitsubishi Economic Research Institute",
							"MESI => Moscow State University of Economics, Statistics and Informatics",
							"METRIC => Modern Economics Training, Research and Innovation Center",
							"MFS => Multinational Finance Society",
							"MGIMO => Moscow State Institute of International Relations",
							"MGUPP => Moscow State University for Food Production",
							"MHHDC => Mahbub-ul-Haq Human Development Center",
							"MIEPA => McKeever Institute of Economic Policy Analysis",
							"MIER => Malaysian Institute of Economic Research",
							"MIT => Massachusetts Institute of Technology",
							"MIX => Microfinance Information Exchange",
							"MLEA => Midwestern Law and Economics Association",
							"MOVE => Consorci Markets, Organizations and Votes in Economics",
							"MSM => Maastricht School of Management",
							"MSSANZ => Modelling and Simulation Society of Australia and New Zealand",
							"MSSES => Moscow School of Social and Economic Sciences",
							"MUST => Misr University for Science and Technology",
							"MWEIG => Midwestern International Economics Group",
							"NAAE => Nigerian Association of Agricultural Economists",
							"NAAFE => North American Association of Fisheries Economists",
							"NAASE => North American Association of Sports Economists",
							"NABARD => National Bank for Agriculture and Rural Development",
							"NABE => National Association for Business Economics",
							"NAEKOR => Russian Independent Agricultural Economics Association",
							"NAFE => National Association of Forensic Economics",
							"NAREA => Northeastern Agricultural and Resource Economics Association",
							"NASB => National Academy of Sciences of Belarus",
							"NASC => Nepal Administrative Staff College",
							"NBEA => Northeast Business and Economics Association",
							"NCAP => National Centre for Agricultural Economics and Policy Research",
							"NCBAE => National College of Business Administration and Economics",
							"NCCEE => North Carolina Council on Economic Eduation",
							"NCER => National Centre for Econometric Research",
							"NCFAP => National Center for Food and Agricultural Policy",
							"NDRI => National Dairy Research Institute",
							"NEA => National Economic Association",
							"NEAK => Northeast Asia Economic Association of Korea",
							"NEPS => Network of European Peace Scientists",
							"NEREC => Network for Economic Research on Electronic Communications",
							"NERI => Nagano Economic Research Institute",
							"NERI => Nanto Economic Research Institute",
							"NERI => Nevin Economic Research Institute",
							"NES => New Economic School",
							"NETA => National Economics Teaching Association",
							"NETT => North East Think Tank of Japan",
							"NEUDC => New England Universities Development Consortium",
							"NFA => Northern Finance Association",
							"NHEA => Nepal Health Economics Association",
							"NIBM => National Institute of Bank Management",
							"NICE => Newports Institute of Communications and Economics",
							"NIDI => Netherlands Interdisciplinary Demographic Institute",
							"NIPS => National Institute for Population Studies",
							"NISER => Nigerian Institute of Social and Economic Research",
							"NISTADS => National Institute of Science, Technology and Development Studies",
							"NITIE => National Institute of Industrial Engineering",
							"NIUA => National Institute of Urban Affairs",
							"NLIHC => National Low Income Housing Coalition",
							"NMIMS => Narsee Monjee Institute of Management Studies",
							"NMIMS => SVKM's Narsee Monjee Institute of Management Studies",
							"NOBE/REF => Network of Border Economics / Red de la Economía Fronteriza",
							"NOBEM => Netherlands Organisation for Research in Business Economics and Management",
							"NRRI => National Regulatory Research Institute",
							"NSDRC => Northwest Socioeconomic Development Research Center",
							"NTA => National Tax Association",
							"NUS => National University of Singapore",
							"NUST => National University of Sciences and Technology",
							"NYU => New York University",
							"NZARES => New Zealand Agricultural and Resource Economics Society",
							"NZESG => New Zealand Econometric Study Group",
							"ODE => Omicron Delta Epsilon",
							"OECD => Organisation for Economic Co-operation and Development",
							"OECD => Organization for Economic Cooperation and Development",
							"OEF => Oxford Economic Forecasting",
							"OIES => Oxford Institute for Energy Studies",
							"OTEFA => Overseas Thai Economic and Finance Association",
							"OUHK => Open University of Hong Kong",
							"PAEP => Employment Observatory Research-Informatics",
							"PAPAIOS => Pan Pacific Association of Input-Output Studies",
							"PECC => Pacific Economic Cooperation Council",
							"PEEHS => Political Economy and Economic History Society",
							"PEF => Progressive Economic Forum",
							"PEKEA => Political and Ethical Knowledge on Economic Acivities Research Programme",
							"PEP => Partnership for Economic Policy",
							"PERC => Property and Environment Research Center",
							"PGSA => Pro Global Science Association",
							"PIPFA => Pakistan Institute of Public Finance Accounts",
							"PKES => Post Keynesian Economics Society",
							"PPIC => Public Policy Institute of California",
							"PRADEC => Prague Development Center",
							"PRI => Policy Research Institute",
							"PRMIA => Professional Risk Managers' International Association",
							"PRRES => Pacific-Rim Real Estate Society",
							"PRSCO => Pacific Regional Science Conference Organization",
							"PSSRU => Personal Social Services Research Unit",
							"QIIR => Qianhai Institute of Innovative Research",
							"RAD => Researchers Alliance for Development",
							"RANEPA => Russian Presidential Academy of National Economy and Public Administration",
							"RAS => Russian Academy of Sciences",
							"RCN => Economic Research Center of Niigata",
							"RDC => Romanian Distribution Committee",
							"RERI => Real Estate Research Institute",
							"RES => Royal Economic Society",
							"RESER => European Association for Research on Service",
							"RFF => Resources for the Future",
							"RFH => Research Foundation for Humanity",
							"RIDGE => Research Institute for Development, Growth, and Economics",
							"RIEF => Research in International Economics and Finance Network",
							"RIES => Research Institute of the East-West Economy & Society",
							"RIETI => Research Institute of Economy, Trade and Industry",
							"RIOE => Research Institute for Ocean Economics",
							"RISE => Research on Improving Systems of Education",
							"RISEBA => Riga International School of Economics and Business Administration",
							"RSA => Regional Studies Association",
							"RSA-Nederland => Regional Science Association, Netherlands Section",
							"RSAI => Regional Science Association International",
							"RSAIBIS => Regional Science Association International, British and Irish Section",
							"RSEE => Russian Society for Ecological Economics",
							"RTI => Research Triangle Institute",
							"RTS => Risk Theory Society",
							"RTT => Romania Think Tank",
							"RUDN => Peoples Friendship University of Russia",
							"RUPRI => Rural Policy Research Institute",
							"RePEc => Research Papers in Economics",
							"Resanet => Research Africa Network",
							"SABE => Society for the Advancement of Behavioral Economics",
							"SADC => Southern African Development Community",
							"SAEA => Southern Agricultural Economics Association",
							"SAEE => Swiss Association for Energy Economics",
							"SAET => Society for the Advancement of Economic Theory",
							"SAFA => Southern African Finance Association",
							"SALE => Scandinavian Association of Law and Economics",
							"SAMA => Saudi Arabian Monetary Agency",
							"SANE => South African New Economics Society",
							"SANEI => South Asia Network of Economic Research Institutes",
							"SASE => Society for the Advancement of Socio-Economics",
							"SASS => School of Advanced Social Studies",
							"SAWTEE => South Asia Watch on Trade, Economics and Environment",
							"SBCA => Society for Benefit-Cost Analysis",
							"SBE => Society of Business Economists",
							"SCE => Society for Computational Economics",
							"SCMHRD => Symbiosis Centre for Management and Human Resource Development",
							"SCW => Society for Social Choice and Welfare",
							"SDAE => Society for the Development of Austrian Economics",
							"SDIC => School of Development Innovation and Change",
							"SDS => System Dynamics Society",
							"SEA => Southern Economic Association",
							"SEA => Spacial Econometrics Association",
							"SEARCA => Southeast Asian Regional Center for Graduate Study and Research in Agriculture",
							"SEBH => Society for European Business History",
							"SED => Society for Economic Dynamics",
							"SEG => Society of Economic Geologists",
							"SEHA => Swedish Economic History Association",
							"SEM => Society for Economic Measurement",
							"SERCI => Society for Economic Research on Copyright Issues",
							"SERI => Samsung Economic Research Institute",
							"SERI => Shikuoka Economic Research Institute",
							"SES => Scottish Economic Society",
							"SESS => Society for the Economic Studies of Securities",
							"SET => Society for Economic Theory",
							"SFS => Society for Financial Studies",
							"SGBED => Society for Global Business and Economic Development",
							"SGCA => Single Global Currency Association",
							"SGE => Society of Government Economists",
							"SHE => Society of Heterodox Economists",
							"SHP => Swiss Household Panel",
							"SID => Society for International Development",
							"SIFR => Institute for Financial Research",
							"SIMT => Stuttgart Institute of Management and Technology",
							"SIOE => Society for Institutional and Organizational Economics",
							"SIPRI => Stockholm International Peace Research Institute",
							"SIRE => Scottish Institute for Research in Economics",
							"SKOPE => Centre on Skills, Knowledge and Organisational Performance",
							"SNDE => Society for Nonlinear Dynamics and Econometrics",
							"SOAS => School of Oriental and African Studies",
							"SOFEW => Southern Forest Economics Workers",
							"SPDC => Social Policy and Development Centre",
							"SPM => Society for Policy Modeling",
							"SQG => Society of Quantitative Gastronomy",
							"SRDC => Social Research and Demonstration Corporation",
							"SRSA => Southern Regional Science Association",
							"SSBF => Society for the Study of Business and Finance",
							"SSSP => Society for the Study of Social Policy",
							"SUNY => Stony Brook University",
							"SUNY => Farmingdale State College",
							"SUNY => State University of New York",
							"SVIM => Sarva Vidyalaya Instritute of Management",
							"SWFA => Southwestern Finance Association",
							"SWUFE => Southwestern University of Finance and Economics",
							"Sa-Dhan => Association of Community Development Finance Institutions",
							"SoFiE => Society for Financial Econometrics",
							"TAFA => Turkish American Finance Association",
							"TBEN => The Black Economists Network",
							"TCER => Tokyo Center for Economic Research",
							"TDRI => Thailand Development Research Institute",
							"TERI => The Energy and Resources Institute",
							"TESDO => The Economic and Social Development Organization",
							"TFA => Taiwan Finance Association",
							"TIES => The Indian Econometric Society",
							"TIES => The International Environmetrics Society",
							"TIPS => Trade and Industrial Policy Secretariat",
							"TPUG => Transportation and Public Utilities Group",
							"TRAPCA => Trade Policy Training Centre in Africa",
							"TSE => Toulouse School of Economics",
							"UACES => University Association for Contemporary European Studies",
							"UCL => University College London",
							"UCLA => University of California-Los Angeles",
							"UCSB => University of California-Santa Barbara",
							"UCSC => University of California-Santa Cruz",
							"UCSD => University of California-San Diego",
							"UEA => Urban Economics Association",
							"UERI => Urban Economic Research Institute",
							"UIBE => University of International Business and Economics",
							"UKNEE => UK Network of Environmental Economists",
							"UMT => University of Management and Technology",
							"UNISA => University of South Africa",
							"UNISZA => Universiti Sultan Zainal Abidin",
							"UPEG => Ukrainian Productivity and Efficiency Group",
							"URPE => Union for Radical Political Economics",
							"USAEE => United States Association for Energy Economics",
							"USSEE => United States Society for Ecological Economics",
							"UTAMU => Uganda Technology And Management University",
							"UTI => Unit Trust of India",
							"VCREME => Vietnam Center of Research in Economics, Management and Environment",
							"VEA => Vietnamese Economics Association",
							"VECON => Vietnamese Economics Network",
							"VIAPI => All-Russian institute of agrarian problems and information theory",
							"VNU => Vietnam National University",
							"WAFA => Washington Area Finance Association",
							"WASCAL => West African Science Service Center on Climate Change and Adapted Land Use",
							"WDR => World Dialogue on Regulation for Network Economies",
							"WEA => World Economics Association",
							"WEF => World Economic Forum",
							"WHEG => Welsh Health Economist Group",
							"WPA => World Psychiatric Association, Section on Mental Health Economics",
							"WPEG => Work Pensions and Labour Economics Study Group",
							"WRIA => Western Risk and Insurance Association",
							"WTO => World Trade Organization",
							"XIME => Xavier Institute of Management and Entrepreneurship",
							"XIMR => Xavier Institute of Management and Research",
							"XJTLU => Xi'an Jiaotong-Liverpool University",
							"XLRI => Xavier Labour Relations Institute",
							"ZEPARU => Zimbabwe Economic Policy Analysis and Research Unit",
							"ZIPAR => Zambia Institute for Policy Analysis and Research",
							"ZISMG => Univeristy of Humanities 'Zaporizhia Institute of State and Municipial Government'",
							"eBRN => E-Business Research Network",
							"iDEAs => International Data Envelopment Analysis Society",
							"iHEA => International Health Economics Association"
							]
					}
				}
			}
		}
	},
    "mappings": {
        "properties": {
        	# Publication title
            "title": { "type": "text" },
        	# Publication abstract
            "abstract": { "type": "text" },
            # Topic (in English, not the JEL code!)
            "jel-labels": { "type": "keyword" },
            # Keywords as a separate field
            "keywords": { "type": "keyword" },
            # Publication date
            "creation_date": { "type": "keyword", "index": False },
            # List of authors
            "authors":  { 
            	"type": "nested", 
          		"properties": {
          			"full_name": { "type": "text" },
          			"first_name": { "type": "text" },
          			"last_name": { "type": "text" },
          			# Affiliation at the time of this publication
          			"institution": { "type": "text" }
          		}
			}
        }
	}
}

ES = Elasticsearch()

ENCODINGS = ['utf-8', 'utf-16-le']

def lines(f):
	handle = None
	for e in ENCODINGS:
		if handle:
			handle.close()
			break
		try:
			handle = io.open(f, 'r', encoding=e)
			for l in handle:
				yield l.strip()
		except:
			logging.debug("Error opening file {} in {}".format(f, e), sys.exc_info()[0])

JEL_CODEMAP = { }
for l in lines("./jel_map"):
	cl = l.split("|")[1:3]
	code = cl[1].strip()
	label = cl[0].replace("Other", "").replace("General", "").replace(":", "").strip()
	JEL_CODEMAP[code] = label

# RE_FIELD_VALUE = re.compile(r"([\w\-]+): (.+)")
RE_FIELD_VALUE = re.compile(r"([^: ]+): ?(.+)")

# RE_DATE_VALUE = re.compile(r"((20[012][0-9])|(19[0-9]{2}))(\-((0?[1-9])|1[0-2])(\-[0-3][0-9])?)?$")
RE_DATE_VALUE = re.compile(r"((20[012][0-9])|(19[0-9]{2}))(\-((0[1-9])|1[0-2])(\-[0-3][0-9])?)?$")

AUTHOR_FIELDS = {
	"Author-Name-First".lower(): 'first_name',
	"Author-Name-Last".lower(): 'last_name',
	"Author-Email".lower(): 'email',
	"Author-Workplace-Name".lower(): 'institution'
}

INST_COUNTER = Counter()

def is_accepted_tpl(val):
	#return val in ["ReDIF-Article 1.0", "ReDIF-Paper 1.0"]
	return True

def jel_labels(val):
	for c in re.split(r';|,| ', val):
		code = c.strip()
		if not code:
			continue
		try:
			yield JEL_CODEMAP[code]
		except KeyError:
			if len(code) == 2:
				try:
					yield JEL_CODEMAP[code + "0"]
				except KeyError:
					logging.error("JEL code not found ({} nor {})".format(code, code + "0"))	

def keywords(val):
	for k in re.split(r';|,', val):
		keyword = k.strip()
		if not keyword:
			continue
		yield keyword

def parse_date(val):
	for f in ['%Y-%m-%d', '%Y-%m', '%Y', '%Y/%m/%d', '%Y/%m', '%m/%d/%Y', '%Y%m%d', '%Y%m']:
		try:
			return datetime.strptime(val, f)
		except ValueError as ve:
			pass
	return None

def parse_repec_file(f):
	tpl = None
	obj = None
	grp, key, txt = None, None, []
	for l in lines(f):
		m = RE_FIELD_VALUE.match(l)
		if m:
			if len(txt) > 0:
				if key and obj:
					obj[key] = '\n'.join(txt)
				key, txt = None, []
			key, val = m.group(1).lower(), m.group(2).strip()
			if len(val) < 1:
				continue
			if key in AUTHOR_FIELDS:
				if grp:
					grp[AUTHOR_FIELDS[key]] = val
			elif key == "Author-Name".lower():
				if grp and obj:
					obj["authors"].append(grp)
				grp = { "full_name": val }
			else:
				if key.endswith("Template-Type".lower()):
					if obj is not None: 
						if grp:
							obj["authors"].append(grp)
						yield obj
						obj = None
					if is_accepted_tpl(val):
						obj = { "type" :  val, "authors": [] }
					grp = None
				elif key in ["Title".lower(), "Abstract".lower()]:
					txt = [val]
				elif obj and key == "Creation-Date".lower():
					date = parse_date(val)
					if date:
						obj["creation-date"] = date
					else:
						logging.warning("Invalid creation date: {}".format(val))
				elif obj and key == "File-URL".lower():
					obj["url"] = val
				elif obj and key == "Classification-JEL".lower():
					obj["jel-labels"] = list(jel_labels(val))
				elif obj and key == "Keywords".lower():
					obj["keywords"] = list(keywords(val))
		elif txt and len(l) > 0:
			txt.append(l)
	if obj is not None: 
		if grp:
			obj["authors"].append(grp)
		yield obj

def yield_bulk_items(d):
	for f in glob.glob("{}/**/*.rdf".format(d)):
		logging.debug("Processing file", f)
		for obj in parse_repec_file(f):
			obj["_index"] = ES_INDEX_PUBLI
			for author in obj["authors"]:
				if "institution" in author:
					INST_COUNTER[author["institution"]] += 1
			yield obj

def parse_repec_root_bulk(p):
	path = Path(p)
	for f in path.iterdir():
		if f.is_dir():
			print("Processing directory", f)
			for success, info in parallel_bulk(ES, yield_bulk_items(f)):
				if not success:
					print('A document failed:', info)

COMPUTE_TOP_INSTITUTIONS = False

if __name__ == "__main__":
	try:
		ES.indices.delete(index=ES_INDEX_PUBLI)
		print("Re-creating index", ES_INDEX_PUBLI)
	except:
		print("Creating index", ES_INDEX_PUBLI)
	ES.indices.create(index=ES_INDEX_PUBLI, body=MAPPING_PUBLI)
	parse_repec_root_bulk("./repec_data/data/")
	print("Index created")
	if COMPUTE_TOP_INSTITUTIONS:
		print("Most popular institutions")
		for k, v in INST_COUNTER.most_common(10000):
			print(k)
