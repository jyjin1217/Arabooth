
const todayChart = async (year, month, day) => {

    const uriOrign = "https://a3df8nbpa2.execute-api.ap-northeast-2.amazonaws.com/v1/log" + "?year=" + year + "&month=" + month + "&day=" + day;
    let response = await fetch(uriOrign, {method:'GET'})
    
    if(response.ok){
      let resJson = await response.json();
  
      let labelArr = ["사용자", "사용중"];
      let dataArr = [0, 0];      
      let maxNum = 0;

      for(let key in resJson) {
          let boothName = resJson[key]['BoothName'];
          if (boothName == '테스트') continue;
  
          let duration = resJson[key]['Duration-sec'];
          if (duration == 'progressing') dataArr[1] += 1;
          else dataArr[0] += 1;
                  
          maxNum += 1;
      }
            
      let maxY = maxNum - (maxNum % 10) + 10; 
  
      let chartParent = document.getElementById("todayChart");
      while (chartParent.firstChild){
        chartParent.removeChild(chartParent.firstChild);
      }
      let newCanvas = document.createElement('canvas');
      chartParent.appendChild(newCanvas);
  
      new Chart(newCanvas, {
        type: 'bar',
        data: {
          labels: labelArr,
          datasets: [{
            label: "총원",
            backgroundColor: "#4e73df",
            hoverBackgroundColor: "#2e59d9",
            borderColor: "#4e73df",
            data: dataArr,
            maxBarThickness: 25,
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
                unit: 'month'
              },
              gridLines: {
                display: false,
                drawBorder: false
              },
              ticks: {
                maxTicksLimit: 6
              }              
            }],
            yAxes: [{
              ticks: {
                min: 0,
                max: maxY,
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
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10,
            callbacks: {
              label: function(tooltipItem, chart) {
                var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
              }
            }
          },
        }
      });
      
      let todayText = document.getElementById('todayText');
      maxNum = (maxNum < 10)? '0' + maxNum : maxNum.toString();
      todayText.innerText = '오늘 사용자(Today) - 총원 : ' + maxNum + '명';
      return true;
    }
    
    alert("Request Fail\n문제가 지속되면 관리자에게 문의해주세요")

    return false;
  }
  