
const enterpriseChart = async (year, month) => {

    const uriOrign = "https://a3df8nbpa2.execute-api.ap-northeast-2.amazonaws.com/v1/log" + "?year=" + year + "&month=" + month;
    let response = await fetch(uriOrign, {method:'GET'})
    
    if(response.ok){
        let resJson = await response.json();

        let map = new Map();
        let maxNum = 0;
        for(let key in resJson) {
            let boothName = resJson[key]['BoothName'];
            if (boothName == '테스트') continue;
  
            let endDate = resJson[key]['EndDate'];
            if (endDate == 'occupied') continue;
            
            let company = resJson[key]['Company'];
            if (map.has(company)) map.set(company, map.get(company) + 1);
            else map.set(company, 1);
            
            maxNum++;
        }
        
        let labelArr = null;
        let dataArr = null;
        if (map.size >= 3) {
            labelArr = ["none", "none", "none", "Etc"];
            dataArr = [0, 0, 0, 0];
        }
        else {
            labelArr = new Array();
            dataArr = new Array();
            for(let i = 0; i < map.size; i++) {
                labelArr.push("none");
                dataArr.push(0);
            }
            labelArr.push("Etc");
            dataArr.push(0);
        }

        map.forEach((value, key) => {
            let curValue = value;
            let curKey = key;
            for(let i = 0; i < labelArr.length - 1; i++) {
                if (curValue > dataArr[i]) {
                    let tempKey = labelArr[i];
                    labelArr[i] = curKey;  
                    curKey = tempKey;

                    let tempNum = dataArr[i];
                    dataArr[i] = curValue;
                    curValue = tempNum;                    
                }
            }            
        });

        let total = 0;
        for(let i = 0; i < dataArr.length - 1; i++) total += dataArr[i];
        dataArr[dataArr.length - 1] = maxNum - total;        
 

        let chartParent = document.getElementById("myPieChart");
        while (chartParent.firstChild){
            chartParent.removeChild(chartParent.firstChild);
        }
        let newCanvas = document.createElement('canvas');
        chartParent.appendChild(newCanvas);

        new Chart(newCanvas, {
            type: 'doughnut',
            data: {
              labels: labelArr,
              datasets: [{
                data: dataArr,
                backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
                hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
                hoverBorderColor: "rgba(234, 236, 244, 1)",
              }],
            },
            options: {
              maintainAspectRatio: false,
              tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                borderColor: '#dddfeb',
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                caretPadding: 10,
              },
              legend: {
                display: true
              },
              cutoutPercentage: 80,
            },
        });

        return true;
    }
    
    return false;
}
