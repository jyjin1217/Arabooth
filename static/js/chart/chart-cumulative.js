
const cumulativeUserChart = async (year) => {  

  const uriOrign = "https://a3df8nbpa2.execute-api.ap-northeast-2.amazonaws.com/v1/log" + "?year=" + year;
  let response = await fetch(uriOrign, {method:'GET'})
  
  if(response.ok){
    let resJson = await response.json();

    let date = new Date();
    let labelArr = null;
    let dataArr = null;
    if (Number(year) < date.getFullYear()){
        labelArr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        dataArr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    }
    else {
        labelArr = new Array();
        dataArr = new Array();
        for(let i = 0; i <= date.getMonth(); i++){                        
            switch(i){
                case 0: labelArr.push("Jan"); break;
                case 1: labelArr.push("Feb"); break;
                case 2: labelArr.push("Mar"); break;
                case 3: labelArr.push("Apr"); break;
                case 4: labelArr.push("May"); break;
                case 5: labelArr.push("Jun"); break;
                case 6: labelArr.push("Jul"); break;
                case 7: labelArr.push("Aug"); break;
                case 8: labelArr.push("Sep"); break;
                case 9: labelArr.push("Oct"); break;
                case 10: labelArr.push("Nov"); break;
                case 11: labelArr.push("Dec"); break;
                default: labelArr.push("none"); break;
            }
            dataArr.push(0);
        }
    }

    for(let key in resJson) {
        let boothName = resJson[key]['BoothName'];
        if (boothName == '테스트') continue;

        let endDate = resJson[key]['EndDate'];
        if (endDate == 'occupied') continue;                    

        let startDate = resJson[key]['StartDate'];
        let useMonth = startDate.split('.')[1];
        let index = Number(useMonth) - 1;

        dataArr[index] += 1;
    }
    
    let chartParent = document.getElementById("myAreaChart");
    while (chartParent.firstChild){
      chartParent.removeChild(chartParent.firstChild);
    }
    let newCanvas = document.createElement('canvas');
    chartParent.appendChild(newCanvas);

    new Chart(newCanvas, {
        type: 'line',
        data: {
            labels: labelArr,
            datasets: [{
            label: "사용자",
            lineTension: 0.3,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: "rgba(78, 115, 223, 1)",
            pointRadius: 3,
            pointBackgroundColor: "rgba(78, 115, 223, 1)",
            pointBorderColor: "rgba(78, 115, 223, 1)",
            pointHoverRadius: 3,
            pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
            pointHoverBorderColor: "rgba(78, 115, 223, 1)",
            pointHitRadius: 10,
            pointBorderWidth: 2,
            data: dataArr,
            }],
        },
        options: {
            maintainAspectRatio: false,
            layout: {
            padding: {
                left: 10,
                right: 25,
                top: 25,
                bottom: 0
            }
            },
            scales: {
            xAxes: [{
                time: {
                  unit: 'date'
                },
                gridLines: {
                  display: false,
                  drawBorder: false
                },
                ticks: {
                  maxTicksLimit: 7
                }
            }],
            yAxes: [{
                ticks: {
                  maxTicksLimit: 5,
                  padding: 10,
                  // Include a dollar sign in the ticks
                  callback: function(value, index, values) {
                      return number_format(value);
                  }
                },
                gridLines: {
                  color: "rgb(234, 236, 244)",
                  zeroLineColor: "rgb(234, 236, 244)",
                  drawBorder: false,
                  borderDash: [2],
                  zeroLineBorderDash: [2]
                }
            }],
            },
            legend: {
                display: false
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: '#6e707e',
                titleFontSize: 14,
                borderColor: '#dddfeb',
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: 'index',
                caretPadding: 10,
                callbacks: {
                    label: function(tooltipItem, chart) {
                      var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                      return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
                    }
                }
            }
        }

    });

    return true;
  }

  return false;
}
