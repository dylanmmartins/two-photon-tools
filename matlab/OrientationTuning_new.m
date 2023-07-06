function oriRespData = OrientationTuning_new(data,plot_flag,save_flag)

%%% Determine orientation tuning of imaged neurons using DFF response
%%% Written MG 160613

%clear
close all
    
if nargin==0
    fprintf("Choose your data file: \n")
    [filename,pathname] = uigetfile('.mat');
    cd(pathname);
    load(filename);
    save_flag = questdlg('Save file?','Dialog box','Yes','No','Yes');
    plot_flag = questdlg('Plot responses?','Dialog box','Responsive','All','None','Responsive');
end

%% load stimulus data
fprintf("Choose your stimulus data file: \n")
[fn, pn] = uigetfile('.mat');
stimdata = importdata(fullfile(pn, fn))

% Parameters
numRep = stimdata.n_repeats;      % number of repeats
numOri = stimdata.n_presentations;     % number of orientations
preTime = stimdata.post_time;     % first part of offTime (not included in analysis due to signal recovery)
offTime = stimdata.pre_time;     % second part of offTime (included in analysis)
onTime = stimdata.on_time;      % stimulus time (sec)
respThresh = 2;  % Threshold to be considered responsive (SD above baseline)
oriThresh = 0.5; % Threshold to be considered orientation tuned (OSI)

% Calculate additional parameters
oriTime = preTime+onTime+offTime;
repTime = oriTime*numOri;
offFrames = round(offTime*data.frameRate);
onFrames = round(onTime*data.frameRate);

% initalize
numCells = size(data.DFF,1);
oriResp = zeros(numCells,numOri,numRep);
oriOff = zeros(numCells,numOri,numRep);
oriDev = zeros(numCells,numOri,numRep);

% Determine orientation preference
for rep = 1:numRep
    for ori = 1:numOri
        currFrame = round(((rep-1)*repTime+(ori-1)*oriTime)*data.frameRate) + 1;
        offResp = mean(data.DFF(:,currFrame:currFrame+offFrames-1),2);
        offDev = std(data.DFF(:,currFrame:currFrame+offFrames-1),0,2);
        onResp = mean(data.DFF(:,currFrame+offFrames:currFrame+offFrames+onFrames-1),2);
        oriResp(:,ori,rep) = onResp-offResp;
        oriOff(:,ori,rep) = offResp;
        oriDev(:,ori,rep) = offDev;
    end
end
meanOriResp = mean(oriResp,3);
meanOffResp = mean(oriOff,3);
meanOriDev = mean(oriDev,3);
[~,oriPref] = max(meanOriResp,[],2);

% Determine responsiveness and tuning
window = 5; % on each side

for cell = 1:numCells
    zScoreVec(cell) = meanOriResp(cell,oriPref(cell))/meanOriDev(cell,oriPref(cell));
    isResp(cell) = zScoreVec(cell)>respThresh;
    pref = meanOriResp(cell,oriPref(cell));
    orth = mean(meanOriResp(cell,[mod(oriPref(cell)-numOri/4-1,numOri)+1 mod(oriPref(cell)+numOri/4-1,numOri)+1]));
    osiVec(cell) = (max([1 pref])-max([1 orth]))/(max([1 pref])+max([1 orth]));
    isTuned(cell) = (isResp(cell)==1) && osiVec(cell)>oriThresh;
end
disp(['Percent responsive (' num2str(respThresh) ' SD over baseline) = ' num2str(mean(isResp)*100) '%']);
disp(['Percent tuned (OSI>' num2str(oriThresh) ') = ' num2str(mean(isTuned)*100) '%']);
data.oriResp = meanOriResp;
data.zScoreVec = zScoreVec;
data.osiVec = osiVec;
data.oriPref = oriPref;
data.isTuned = isTuned;

if strcmp(save_flag,'Yes') 
    eval(['save ' filename ' data'])
end

% plot responses
if ~strcmp(plot_flag,'None')
    for n = 1:numCells
        if strcmp(plot_flag,'All') || isResp(n)
            ori = oriPref(n);
            for rep = 1:numRep
                currFrame = round(((rep-1)*repTime+(ori-1)*oriTime)*data.frameRate)+1;
                prefResp(n,:,rep) = data.DFF(n,currFrame:currFrame+offFrames+onFrames-1);
            end
            subplot(2,2,1)
            pref_mean = mean(prefResp(n,:,:),3);
            pref_SE = std(prefResp(n,:,:),[],3)/sqrt(numRep);
            plotMin = floor(min(pref_mean-pref_SE)/100)*100;
            plotMax = ceil(max(pref_mean+pref_SE)/100)*100;
            hold on
            rectangle('Position',[0,plotMin,onTime,plotMax-plotMin],'FaceColor',[0.9 0.9 0.9],'EdgeColor',[0.9 0.9 0.9])
            plot(linspace(-offTime,onTime,length(pref_mean)),pref_mean,'linewidth',3,'color',[0 0.5 0.8])
            plot(linspace(-offTime,onTime,length(pref_mean)),pref_mean-pref_SE,'linewidth',1.5,'color',[0 0.5 0.8])
            plot(linspace(-offTime,onTime,length(pref_mean)),pref_mean+pref_SE,'linewidth',1.5,'color',[0 0.5 0.8])
            ylabel('DF/F')
            xlabel('Time (sec)')
            title(['Onset response (preferred): Z-Score = ' num2str(zScoreVec(n)) ', OSI = ' num2str(osiVec(n))])
            
            subplot(2,2,2)
            % set min amplitude on polar plot
            if max(meanOriResp(n,:))<50
                theta = [0 2*pi];
                pho = [50 50]; % set min
                h1 = polar(theta,pho); % plot white point
                set(h1,'color',[1 1 1])
                theta = [0 2*pi];
                hold on
            end
            theta = [0:360/numOri:360]*pi/180;
            pho = [meanOriResp(n,:) meanOriResp(n,1)];
            pho(pho<0) = 0; % rectify
            h1 = polar(theta,pho);
            set(h1,'linewidth',2,'color',[0 0.5 0.8])
            title('Orientation tuning')
            
            subplot(2,2,[3 4])
            plotMin = floor(min(data.DFF(n,:))/100)*100;
            plotMax = ceil(max(data.DFF(n,:))/100)*100;
            hold on
            plot(data.DFF(n,:))
            colormatrix = jet(12);
            for rep = 1:numRep
                for ori = 1:numOri
                    currStim = round(((rep-1)*repTime+(ori-1)*oriTime+preTime+offTime)*data.frameRate);
                    plot(linspace(currStim,currStim+onFrames,100),(plotMin+25)*ones(1,100),'color',colormatrix(ori,:),'linewidth',2)
                end
            end
            xlim([1 size(data.DFF,2)])
            xlabel('Time (sec)')
            ylabel ('DF/F')
            title(['DF/F trace: Neuron ' num2str(n) '/' num2str(size(data.DFF,1))])
            set(gcf,'color',[1 1 1])
            set(gcf,'position',[150 200 1600 800])
            pause
            close
        end
    end
end

