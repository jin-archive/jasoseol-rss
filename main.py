from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import time
from urllib.parse import urljoin

def generate_rss():
    # 자소설닷컴 채용공고 검색 페이지 URL
    url = "https://jasoseol.com/search"
    
    # 가상 브라우저(Headless Chrome) 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless') # 화면을 띄우지 않고 백그라운드에서 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("페이지 로딩 중...")
        driver.get(url)
        # 자소설닷컴은 자바스크립트로 데이터를 불러오므로 넉넉히 대기합니다.
        time.sleep(7) 
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # RSS 기본 정보 셋팅
        fg = FeedGenerator()
        fg.title('자소설닷컴 채용공고')
        fg.link(href=url, rel='alternate')
        fg.description('자소설닷컴 검색 페이지의 최신 채용공고 RSS 피드입니다.')
        fg.language('ko')
        
        # 채용 공고 카드 링크 추출
        # 자소설닷컴의 채용공고 상세 페이지는 보통 '/recruit/공고번호' 형태의 주소를 가집니다.
        job_links = soup.select('a[href*="/recruit/"]')
        
        # 만약 URL 패턴이 바뀌었을 경우를 대비해 <a> 태그 전체를 백업으로 탐색
        if not job_links:
            job_links = soup.select('a')

        added_links = set()
        count = 0
        
        for a_tag in job_links:
            href = a_tag.get('href', '')
            # 하위 태그들의 텍스트를 공백 단위로 이어 붙임 (기업명 + 공고명 + 직무 등이 합쳐짐)
            title_text = a_tag.get_text(separator=' ', strip=True)
            
            # 네비게이션 메뉴 등 불필요한 태그 필터링
            if len(title_text) < 5 or "로그인" in title_text or "회원가입" in title_text or "채팅" in title_text:
                continue
                
            # 실제 채용공고 링크로 추정되는 항목만 추가
            if '/recruit' in href or '/employ' in href:
                link = urljoin("https://jasoseol.com", href)
                
                # 중복 등록 방지
                if link not in added_links:
                    added_links.add(link)
                    
                    fe = fg.add_entry()
                    fe.title(title_text)
                    fe.link(href=link)
                    fe.description(f"<b>채용 공고 상세:</b> {title_text}")
                    fe.guid(link)
                    count += 1
                    
        fg.rss_file('rss.xml')
        print(f"✅ rss.xml 파일이 성공적으로 생성되었습니다. (총 {count}개의 공고 파싱 완료)")
        
    except Exception as e:
        print(f"❌ 크롤링 중 에러 발생: {e}")
    finally:
        driver.quit() # 메모리 누수를 막기 위해 브라우저 강제 종료

if __name__ == "__main__":
    generate_rss()
